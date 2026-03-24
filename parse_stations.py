import json

raw_markdown = """
| Adungosi | Teso South, Busia |
| Ahero | Nyando, Kisumu |
| Amagoro OCPD | Teso North, Busia |
| Arror | Marakwet West, Elgeyo-Marakwet |
| Bahati | Bahati, Nakuru |
| Bamburi | Kisauni, Mombasa |
| Baricho | Kirinyaga East, Kirinyaga |
| Baringo OCPD | Baringo Central, Baringo |
| Bondo OCPD | Bondo, Siaya |
| Bungoma Hotline | Bungoma Central, Bungoma |
| Bura | Tana North, Tana River |
| Buruburu | Embakasi West, Nairobi |
| Busia Hotline | Busia Township, Busia |
| Butere | Butere, Kakamega |
| Capital Hill Post | Starehe, Nairobi |
| Central PPO Office | Nyeri Central, Nyeri |
| Changamwe | Changamwe, Mombasa |
| Cherangani | Cherangany, Trans Nzoia |
| Chuka | Chuka/Igambang’ombe, Tharaka Nithi |
| Diani | Msambweni, Kwale |
| Eldoret | Kapseret, Uasin Gishu |
| Elementaita Police Post | Gilgil, Nakuru |
| Embakasi OCPD | Embakasi East, Nairobi |
| Embu Hotline | Embu West, Embu |
| Funyula | Funyula, Busia |
| Garbatulla | Garbatulla, Isiolo |
| Garissa Hotline | Garissa Township, Garissa |
| Gatundu | Gatundu South, Kiambu |
| Gilgil | Gilgil, Nakuru |
| Githunguri | Githunguri, Kiambu |
| Gucha OCPD | Gucha, Kisii |
| Hardy | Langata, Nairobi |
| Hola | Tana River, Tana River |
| Homa Bay Hotline | Homa Bay Town, Homa Bay |
| Homabay OCPD | Homa Bay Town, Homa Bay |
| Igoji Police Post | Igoji, Meru |
| Ijara OCPD | Ijara, Garissa |
| Ijara Police | Ijara, Garissa |
| Jamhuri Police Post | Dagoretti South, Nairobi |
| Jogoo Road | Makadara, Nairobi |
| Juja | Juja, Kiambu |
| Kabati | Murang’a South, Murang’a |
| Kabete | Kabete, Kiambu |
| Kahawa Sukari | Ruiru, Kiambu |
| Kakamega OCPD | Kakamega Central, Kakamega |
| Kandara | Kandara, Murang’a |
| Kangema | Kangema, Murang’a |
| Kaptembwa | Nakuru West, Nakuru |
| Kapsowar | Marakwet West, Elgeyo-Marakwet |
| Karatina | Mathira East, Nyeri |
| Karen | Langata, Nairobi |
| Kasarani | Kasarani, Nairobi |
| Kericho | Kericho East, Kericho |
| Keroka | Masaba North, Nyamira |
| Kiambu Hotline | Kiambu Township, Kiambu |
| Kianyaga | Kirinyaga East, Kirinyaga |
| Kibwezi | Kibwezi East, Makueni |
| Kiganjo | Nyeri South, Nyeri |
| Kigumo | Kigumo, Murang’a |
| Kikuyu | Kikuyu, Kiambu |
| Kilgoris | Transmara West, Narok |
| Kilifi OCPD | Kilifi North, Kilifi |
| Kilimani | Dagoretti North, Nairobi |
| Kilome | Kilome, Makueni |
| Kimende Patrol Base | Lari, Kiambu |
| Kimilili | Kimilili, Bungoma |
| Kiminini | Kiminini, Trans Nzoia |
| Kinango | Kinango, Kwale |
| Kipipiri | Kipipiri, Nyandarua |
| Kiriani Police Post | Imenti South, Meru |
| Kisumu OCPD | Kisumu Central, Kisumu |
| Kitale Hotline | Trans Nzoia West, Trans Nzoia |
| Kitui OCPD | Kitui Central, Kitui |
| Kuria OCPD | Kuria East, Migori |
| Kwale OCPD | Matuga, Kwale |
| Kwhisero OCPP | Kwhisero, Kakamega |
| Lamu OCPD Office | Lamu West, Lamu |
| Lanet | Nakuru North, Nakuru |
| Langata OCPD | Langata, Nairobi |
| Lari | Lari, Kiambu |
| Likoni | Likoni, Mombasa |
| Lolgorian | Transmara West, Narok |
| Luanda | Luanda, Vihiga |
| Lugari OCPD | Lugari, Kakamega |
| Lungalunga | Lungalunga, Kwale |
| Lwala | Bondo, Siaya |
| Madogo | Tana North, Tana River |
| Magumu | Nyandarua South, Nyandarua |
| Makongeni | Thika West, Kiambu |
| Makueni Hotline | Makueni, Makueni |
| Makupa | Mvita, Mombasa |
| Malaba | Teso North, Busia |
| Malakisi | Sirisia, Bungoma |
| Malindi | Malindi, Kilifi |
| Mandera OCPD | Mandera East, Mandera |
| Maragua | Maragua, Murang’a |
| Marakwet OCPD | Marakwet East, Elgeyo-Marakwet |
| Mariakani | Kaloleni, Kilifi |
| Marigat | Baringo South, Baringo |
| Masalani | Ijara, Garissa |
| Mathare | Mathare, Nairobi |
| Matunda | Likuyani, Kakamega |
| Maua | Igembe South, Meru |
| Mbooni | Mbooni, Makueni |
| Merti | Merti, Isiolo |
| Meru Central Hotline | Imenti North, Meru |
| Meru North OCPD | Igembe North, Meru |
| Meru South OCPD | Tharaka Nithi, Meru South |
| Migwani | Mwingi West, Kitui |
| Mikinduri | Tigania East, Meru |
| Milangine | Nyandarua Central, Nyandarua |
| Modogashe | Lagdera, Garissa |
| Moi’s Bridge | Soy, Uasin Gishu |
| Molo OCPD | Molo, Nakuru |
| Mombasa Central | Mvita, Mombasa |
| Moyale | Moyale, Marsabit |
| Msambweni | Msambweni, Kwale |
| Mt Elgon OCPD | Mt Elgon, Bungoma |
| Mtito Andei | Kibwezi East, Makueni |
| Mukurwe-Ini | Mukurweini, Nyeri |
| Mumias | Mumias West, Kakamega |
| Murang’a Hotline | Murang’a East, Murang’a |
| Muthaiga | Mathare, Nairobi |
| Mweiga | Kieni West, Nyeri |
| Mwingi | Mwingi Central, Kitui |
| Nairobi Central | Starehe, Nairobi |
| Nairobi Industrial Area | Makadara, Nairobi |
| Naivasha | Naivasha, Nakuru |
| Nakuru | Nakuru Town East, Nakuru |
| Narok | Narok North, Narok |
| Naromoru | Kieni East, Nyeri |
| Nchiru | Tigania West, Meru |
| Ndaragwa | Ndaragwa, Nyandarua |
| Njabini | Kinangop, Nyandarua |
| Njoro | Njoro, Nakuru |
| Nkubu | Imenti South, Meru |
| Ntumu | Tigania West, Meru |
| Nyahururu | Laikipia West, Laikipia |
| Nyali | Nyali, Mombasa |
| Nyamira | Nyamira North, Nyamira |
| Nyandarua Hotline | Nyandarua Central, Nyandarua |
| Nyando OCPD | Nyando, Kisumu |
| Nyeri Hotline | Nyeri Central, Nyeri |
| Ol Joro Orok | Ol Joro Orok, Nyandarua |
| Ol Kalou | Ol Kalou, Nyandarua |
| Othaya | Othaya, Nyeri |
| Oyugis | Rachuonyo South, Homa Bay |
| Pangani | Starehe, Nairobi |
| Parklands | Westlands, Nairobi |
| Port Victoria | Bunyala, Busia |
| Rachuonyo | Rachuonyo North, Homa Bay |
| Rhamu | Mandera North, Mandera |
| Riruta | Dagoretti South, Nairobi |
| Ruiru | Ruiru, Kiambu |
| Runyenjes | Embu East, Embu |
| Saba Saba | Murang’a South, Murang’a |
| Sagana | Kirinyaga West, Kirinyaga |
| Salama | Kilome, Makueni |
| Serem | Vihiga, Vihiga |
| Sericho | Isiolo North, Isiolo |
| Shauri Moyo | Kamukunji, Nairobi |
| Siaya | Siaya, Siaya |
| Solai | Rongai, Nakuru |
| Sololo | Sololo, Marsabit |
| Spring Valley | Westlands, Nairobi |
| Subukia | Subukia, Nakuru |
| Sultan Hamud | Kilome, Makueni |
| Taita Taveta | Taveta, Taita Taveta |
| Tambach | Keiyo North, Elgeyo-Marakwet |
| Tana OCPD | Tana Delta, Tana River |
| Taru | Kinango, Kwale |
| Taveta | Taveta, Taita Taveta |
| Teso Hotline | Teso South, Busia |
| Thika | Thika West, Kiambu |
| Thindigua Patrol Base | Kiambu Town, Kiambu |
| Tigania | Tigania East, Meru |
| Tigoni | Limuru, Kiambu |
| Timau | Buuri, Meru |
| Tot | Marakwet East, Elgeyo-Marakwet |
| Trans-Mara OCPD | Transmara East, Narok |
| Turbo | Turbo, Uasin Gishu |
| Ukwala | Ugenya, Siaya |
| Vihiga OCPD | Vihiga, Vihiga |
| Voi | Voi, Taita Taveta |
| Wajir OCPD | Wajir East, Wajir |
| Wajir Police Station | Wajir East, Wajir |
| Wanguru | Kirinyaga Central, Kirinyaga |
| Watamu | Kilifi North, Kilifi |
| Webuye | Webuye East, Bungoma |
| Wundanyi | Wundanyi, Taita Taveta |
| Yala | Gem, Siaya |
"""

subcounty_map = {}
for line in raw_markdown.strip().split('\n'):
    if not line.strip() or '|' not in line:
        continue
    parts = line.split('|')
    if len(parts) >= 3:
        station = parts[1].strip()
        subcounty_raw = parts[2].strip()
        # Some are "Subcounty, County", some are just "Subcounty"
        subcounty = subcounty_raw.split(',')[0].strip()
        
        if subcounty not in subcounty_map:
            subcounty_map[subcounty] = []
        subcounty_map[subcounty].append(station)

output = "export const POLICE_STATIONS_BY_SUBCOUNTY = " + json.dumps(subcounty_map, indent=2) + ";\n"

with open(r'd:\SuraSmart_Project\frontend\web\src\constants\kenyaPoliceStations.js', 'w') as f:
    f.write(output)
print("Success")
