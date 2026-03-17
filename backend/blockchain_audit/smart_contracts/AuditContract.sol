// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title AuditContract
 * @dev Sura Smart – Blockchain Audit Trail for Missing Person Registry
 *
 * TRD 5.1.2: All database queries logged immutably on-chain.
 * TRD 5.2.1: Only hashed/anonymised PII stored on-chain (never plaintext).
 * TRD 4.2.2: Permission-based access control for audit reads.
 * TRD 8:     BIPA/GDPR-compliant data retention management.
 */
contract AuditContract {

    // ─── Data Structures ────────────────────────────────────────────────────

    struct AuditRecord {
        string  search_id;
        string  user_id_hash;
        string  user_role_hash;
        string  query_type_hash;
        string  database_searched_hash;
        bool    match_found;
        bool    consent_verified;
        string  timestamp;
        string  data_retention_expiry;
        string  version;
        string  transaction_hash;
        bool    exists;
    }

    // ─── State Variables ─────────────────────────────────────────────────────

    address public owner;

    /// @dev Authorised addresses allowed to write audit records.
    mapping(address => bool) public authorisedAuditors;

    /// @dev Primary store: search_id => AuditRecord
    mapping(string => AuditRecord) private auditRecords;

    /// @dev Sequential index for event-based retrieval
    string[] private searchIds;

    // ─── Events ──────────────────────────────────────────────────────────────

    event AuditLogged(
        string  indexed search_id,
        string  user_id_hash,
        string  user_role_hash,
        bool    match_found,
        bool    consent_verified,
        string  timestamp,
        string  data_retention_expiry
    );

    event AuditorAuthorised(address indexed auditor);
    event AuditorRevoked(address indexed auditor);

    // ─── Modifiers ───────────────────────────────────────────────────────────

    modifier onlyOwner() {
        require(msg.sender == owner, "AuditContract: caller is not owner");
        _;
    }

    modifier onlyAuthorised() {
        require(
            authorisedAuditors[msg.sender] || msg.sender == owner,
            "AuditContract: caller not authorised"
        );
        _;
    }

    // ─── Constructor ─────────────────────────────────────────────────────────

    constructor() {
        owner = msg.sender;
        authorisedAuditors[msg.sender] = true;
    }

    // ─── Admin Functions ─────────────────────────────────────────────────────

    /**
     * @notice Grant audit-write permission to an address.
     * @param auditor Address of the backend service account.
     */
    function authoriseAuditor(address auditor) external onlyOwner {
        authorisedAuditors[auditor] = true;
        emit AuditorAuthorised(auditor);
    }

    /**
     * @notice Revoke audit-write permission from an address.
     */
    function revokeAuditor(address auditor) external onlyOwner {
        authorisedAuditors[auditor] = false;
        emit AuditorRevoked(auditor);
    }

    // ─── Core Audit Functions ────────────────────────────────────────────────

    /**
     * @notice Record an immutable audit entry for a search operation.
     *
     * TRD 5.1.2: Called by the Django backend (BlockchainAuditor.log_audit_async)
     * after every facial-recognition / missing-person search.
     *
     * @param _search_id               Unique UUID for the search event.
     * @param _user_id_hash            SHA-256 hash of the acting user's ID.
     * @param _user_role_hash          SHA-256 hash of the user's role.
     * @param _query_type_hash         SHA-256 hash of the query type.
     * @param _database_searched_hash  SHA-256 hash of the targeted database.
     * @param _match_found             Whether a facial match was found.
     * @param _consent_verified        Whether user consent was confirmed.
     * @param _timestamp               ISO-8601 UTC timestamp of the operation.
     * @param _data_retention_expiry   ISO-8601 UTC expiry for auto-purge.
     * @param _version                 Record schema version string.
     */
    function logAudit(
        string calldata _search_id,
        string calldata _user_id_hash,
        string calldata _user_role_hash,
        string calldata _query_type_hash,
        string calldata _database_searched_hash,
        bool            _match_found,
        bool            _consent_verified,
        string calldata _timestamp,
        string calldata _data_retention_expiry,
        string calldata _version
    ) external onlyAuthorised {
        require(bytes(_search_id).length > 0, "AuditContract: empty search_id");
        require(!auditRecords[_search_id].exists, "AuditContract: duplicate search_id");

        // Compute a deterministic on-chain hash to serve as the tx reference.
        string memory tx_hash = _computeRecordHash(
            _search_id, _user_id_hash, _timestamp
        );

        auditRecords[_search_id] = AuditRecord({
            search_id:               _search_id,
            user_id_hash:            _user_id_hash,
            user_role_hash:          _user_role_hash,
            query_type_hash:         _query_type_hash,
            database_searched_hash:  _database_searched_hash,
            match_found:             _match_found,
            consent_verified:        _consent_verified,
            timestamp:               _timestamp,
            data_retention_expiry:   _data_retention_expiry,
            version:                 _version,
            transaction_hash:        tx_hash,
            exists:                  true
        });

        searchIds.push(_search_id);

        emit AuditLogged(
            _search_id,
            _user_id_hash,
            _user_role_hash,
            _match_found,
            _consent_verified,
            _timestamp,
            _data_retention_expiry
        );
    }

    /**
     * @notice Retrieve an audit record by its search_id.
     *
     * TRD 4.2.2: Only authorised addresses can read records.
     */
    function getAudit(string calldata _search_id)
        external
        view
        onlyAuthorised
        returns (AuditRecord memory)
    {
        require(auditRecords[_search_id].exists, "AuditContract: record not found");
        return auditRecords[_search_id];
    }

    /**
     * @notice Verify that an audit record exists and return key integrity fields.
     */
    function verifyAudit(string calldata _search_id)
        external
        view
        onlyAuthorised
        returns (
            bool   exists,
            string memory tx_hash,
            string memory timestamp
        )
    {
        AuditRecord storage rec = auditRecords[_search_id];
        return (rec.exists, rec.transaction_hash, rec.timestamp);
    }

    /**
     * @notice Returns the total number of audit records stored.
     */
    function getAuditCount() external view onlyAuthorised returns (uint256) {
        return searchIds.length;
    }

    /**
     * @notice Returns the search_id at a given index (for sequential iteration).
     */
    function getSearchIdByIndex(uint256 index)
        external
        view
        onlyAuthorised
        returns (string memory)
    {
        require(index < searchIds.length, "AuditContract: index out of bounds");
        return searchIds[index];
    }

    // ─── Internal Helpers ────────────────────────────────────────────────────

    /**
     * @dev Produces a compact deterministic hash string (hex) from key fields.
     *      Used as the simulated transaction_hash for development builds.
     */
    function _computeRecordHash(
        string memory a,
        string memory b,
        string memory c
    ) internal pure returns (string memory) {
        bytes32 h = keccak256(abi.encodePacked(a, b, c));
        return _bytes32ToHexString(h);
    }

    function _bytes32ToHexString(bytes32 data)
        internal
        pure
        returns (string memory)
    {
        bytes memory hexChars = "0123456789abcdef";
        bytes memory result = new bytes(66);
        result[0] = "0";
        result[1] = "x";
        for (uint256 i = 0; i < 32; i++) {
            result[2 + i * 2]     = hexChars[uint8(data[i] >> 4)];
            result[3 + i * 2]     = hexChars[uint8(data[i] & 0x0f)];
        }
        return string(result);
    }
}
