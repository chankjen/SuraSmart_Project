import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Crypto from 'expo-crypto'; // Standard library for basic crypto if no WebAuthn available on React Native
import NetInfo from '@react-native-community/netinfo';
// import api from './api'; // Uncomment when plugging into actual app

const QUEUE_STORAGE_KEY = '@offline_signature_queue';

/**
 * Service to handle cryptographic signing of case closures
 * either online or queued for offline sync.
 * Matches TRD §6.1 Offline Contingency logic.
 */
class OfflineSignatureService {
    /**
     * Generates a cryptographic signature and queues it locally.
     */
    async signCaseClosure(caseId, userCredentials) {
        try {
            // 1. Fetch a nonce from the server if online, otherwise generate locally
            let nonce = await this.getNonceLocally();

            // 2. Create the payload to be signed
            const timestamp = new Date().toISOString();
            const payloadString = `${caseId}:${nonce}:${timestamp}`;

            // 3. Cryptographically sign the payload.
            // MVP Prototype: Simulating Secure Enclave / FIDO2 signature using SHA-256 for demonstration.
            // TRD §6.1 requires WebAuthn / FIDO2 keys stored on the officer's mobile device secure enclave.
            const signatureDigest = await Crypto.digestStringAsync(
                Crypto.CryptoDigestAlgorithm.SHA256,
                `${payloadString}:${userCredentials.privateKeyPlaceholder}`
            );

            const signaturePayload = {
                case_id: caseId,
                nonce: nonce,
                signed_at: timestamp,
                signature_payload: JSON.stringify({ digest: signatureDigest, algorithm: 'SHA-256-SIMULATED' }),
            };

            // 4. Queue the signature locally
            await this.queueSignature(signaturePayload);

            // 5. Attempt Immediate Sync
            await this.syncQueue();

            return true;
        } catch (error) {
            console.error('Error signing case offline:', error);
            throw error;
        }
    }

    /**
     * Fallback pseudo-random nonce for true offline scenarios
     */
    async getNonceLocally() {
        const randomBytes = await Crypto.getRandomBytesAsync(16);
        return Array.from(randomBytes).map(b => b.toString(16).padStart(2, '0')).join('');
    }

    async queueSignature(payload) {
        const queueStr = await AsyncStorage.getItem(QUEUE_STORAGE_KEY);
        const queue = queueStr ? JSON.parse(queueStr) : [];
        queue.push(payload);
        await AsyncStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(queue));
    }

    /**
     * Checks network state and syncs the queue if online.
     * TRD §6.1: Once connectivity >100kbps is detected, the sync agent pushes the signature to the main chain.
     */
    async syncQueue() {
        const netInfo = await NetInfo.fetch();

        // Check if connected and internet is reachable
        if (!netInfo.isConnected || !netInfo.isInternetReachable) {
            console.log('Device is offline. Signatures will remain in the secure queue.');
            return;
        }

        const queueStr = await AsyncStorage.getItem(QUEUE_STORAGE_KEY);
        const queue = queueStr ? JSON.parse(queueStr) : [];

        if (queue.length === 0) return;

        const remainingQueue = [];

        for (const signature of queue) {
            try {
                // Sync via API (Commented out actual fetch for prototype, would use axios or fetch)
                /*
                const response = await api.post('/api/facial-recognition/offline-signatures/sync_signature/', signature);
                
                if (response.data.status === 'synced_with_review') {
                  console.warn('Signature synced with conflict:', response.data.message);
                } else {
                  console.log('Successfully synced signature for case:', signature.case_id);
                }
                */
                console.log(`[PROTOTYPE] Synced signature for case ${signature.case_id} to backend.`);
            } catch (error) {
                console.error('Failed to sync signature for case', signature.case_id, error);
                // Keep in queue if network error or server down.
                if (error.response && error.response.status >= 400 && error.response.status < 500) {
                    console.warn('Dropping invalid signature payload:', signature.case_id);
                } else {
                    remainingQueue.push(signature);
                }
            }
        }

        await AsyncStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(remainingQueue));
    }
}

export default new OfflineSignatureService();
