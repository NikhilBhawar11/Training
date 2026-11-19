"""
Trek Data provider for GadKille Maharashtra Fort Explorer.
Contains structured Trek Card details for forts:
- height
- base_village
- time_to_climb
- water
- night_stay
- wikipedia_attribution & source_url
"""

import json
from pathlib import Path
from app.tools import haversine_distance, load_town_coordinates

BASE_DIR = Path(__file__).resolve().parent.parent
TREK_CARDS_FILE = BASE_DIR / "data" / "trek_cards.json"
RECORDS_FILE = BASE_DIR / "data" / "records.json"

TREK_DATA_MASTER = [
    {
        "fort_name": "Harishchandragad",
        "district": "Ahmednagar",
        "latitude": 19.388239,
        "longitude": 73.77594,
        "height_ft": 4670,
        "height": "4,670 ft (1,423 m)",
        "base_village": "Pachnai / Khireshwar",
        "time_to_climb": "2.5 - 3 hours (Pachnai) / 5 - 6 hours (Khireshwar)",
        "water": "Potable sweet water available in temple cisterns and Kedareshwar cave year-round.",
        "night_stay": "Harishchandreshwar temple caves comfortably accommodate 35-40 trekkers; camping permitted.",
        "difficulty": "Moderate to Strenuous",
        "source_url": "https://en.wikipedia.org/wiki/Harishchandragad",
        "highlights": "Konkan Kada, Kedareshwar Cave Temple, Taramati Peak"
    },
    {
        "fort_name": "Ankai Fort",
        "district": "Nashik",
        "latitude": 20.18722,
        "longitude": 74.447639,
        "height_ft": 3182,
        "height": "3,182 ft (970 m)",
        "base_village": "Ankai",
        "time_to_climb": "1.5 - 2 hours",
        "water": "Rock-cut water cisterns on top; carry drinking water for trekking.",
        "night_stay": "Caves on the fort provide shelter for 20 trekkers; homestays available in base village.",
        "difficulty": "Easy to Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Ankai_Fort",
        "highlights": "Twin fort with Tankai, ancient rock-cut Jain caves, Manmad view"
    },
    {
        "fort_name": "Patta Fort",
        "district": "Ahmednagar",
        "latitude": 19.707278,
        "longitude": 73.836278,
        "height_ft": 4562,
        "height": "4,562 ft (1,390 m)",
        "base_village": "Kokanwadi / Pattawadi",
        "time_to_climb": "1.5 - 2 hours",
        "water": "Freshwater cisterns on the plateau; filter before drinking or carry water.",
        "night_stay": "Patta temple and ashram atop the fort accommodate 25-30 people comfortably.",
        "difficulty": "Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Patta_Fort",
        "highlights": "Vishramgad heritage where Chhatrapati Shivaji Maharaj rested, scenic plateau"
    },
    {
        "fort_name": "Bitangad",
        "district": "Ahmednagar",
        "latitude": 19.6538306,
        "longitude": 73.7861417,
        "height_ft": 3560,
        "height": "3,560 ft (1,085 m)",
        "base_village": "Maldara",
        "time_to_climb": "1 - 1.5 hours",
        "water": "Cistern at the base; water is scarce on top, carry 2-3 liters of water.",
        "night_stay": "Small summit cave shelters 4-5 trekkers; base village Maldara homestays recommended.",
        "difficulty": "Moderate (technical rock scramble at top)",
        "source_url": "https://en.wikipedia.org/wiki/Bitangad",
        "highlights": "Pinnacle view, peaceful offbeat trail near Kalsubai range"
    },
    {
        "fort_name": "Alang",
        "district": "Nashik",
        "latitude": 19.5827,
        "longitude": 73.6612,
        "height_ft": 4852,
        "height": "4,852 ft (1,479 m)",
        "base_village": "Ambewadi / Udadhawane",
        "time_to_climb": "4 - 5 hours",
        "water": "11 rock-cut water cisterns; water available year-round.",
        "night_stay": "Spacious summit cave accommodates 35-40 trekkers comfortably.",
        "difficulty": "Challenging / Technical (ropes & climbing harness required)",
        "source_url": "https://en.wikipedia.org/wiki/Alang_Fort",
        "highlights": "Part of prestigious AMK (Alang-Madan-Kulang) trek; dramatic cliffs"
    },
    {
        "fort_name": "Kulang",
        "district": "Nashik",
        "latitude": 19.5939,
        "longitude": 73.6264,
        "height_ft": 4822,
        "height": "4,822 ft (1,470 m)",
        "base_village": "Kulangwadi",
        "time_to_climb": "3.5 - 4 hours",
        "water": "Potable freshwater cisterns available on top year-round.",
        "night_stay": "Huge rock-cut cave on summit comfortably accommodates 40-50 trekkers.",
        "difficulty": "Challenging (steep continuous stone steps)",
        "source_url": "https://en.wikipedia.org/wiki/Kulang_Fort",
        "highlights": "Highest climb from base to summit in Maharashtra Sahyadris"
    },
    {
        "fort_name": "Harihar Fort",
        "district": "Nashik",
        "latitude": 19.9044,
        "longitude": 73.5042,
        "height_ft": 3676,
        "height": "3,676 ft (1,120 m)",
        "base_village": "Nirgudpada / Harshewadi",
        "time_to_climb": "2 - 2.5 hours",
        "water": "Water cisterns near summit temple; carry clean drinking water.",
        "night_stay": "Small cave accommodates 5-6 people; abundant local homestays in Nirgudpada.",
        "difficulty": "Moderate to Thrilling (80-degree vertical rock-cut stairs)",
        "source_url": "https://en.wikipedia.org/wiki/Harihar_fort",
        "highlights": "Iconic Scottish-gothic rock staircase with carved thumb notches"
    },
    {
        "fort_name": "Salher",
        "district": "Nashik",
        "latitude": 20.7225,
        "longitude": 73.9419,
        "height_ft": 5140,
        "height": "5,140 ft (1,567 m)",
        "base_village": "Salher / Waghambe",
        "time_to_climb": "2.5 - 3 hours",
        "water": "Gangasagar lake and clean rock-cut water cisterns on top.",
        "night_stay": "Parshuram temple and caves at summit accommodate 35+ trekkers.",
        "difficulty": "Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Salher",
        "highlights": "Highest fort in Maharashtra; site of legendary Maratha-Mughal battle"
    },
    {
        "fort_name": "Ramsej",
        "district": "Nashik",
        "latitude": 20.0894,
        "longitude": 73.7997,
        "height_ft": 3273,
        "height": "3,273 ft (998 m)",
        "base_village": "Peth / Bhorgad",
        "time_to_climb": "1 - 1.5 hours",
        "water": "Rock-cut water tanks on top; carry potable drinking water.",
        "night_stay": "Ram Mandir cave on the fort can accommodate 15-20 trekkers.",
        "difficulty": "Easy to Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Ramsej",
        "highlights": "Historic fortress that resisted Mughal siege for 6 years"
    },
    {
        "fort_name": "Ratangad",
        "district": "Ahmednagar",
        "latitude": 19.5,
        "longitude": 73.69,
        "height_ft": 4255,
        "height": "4,255 ft (1,297 m)",
        "base_village": "Ratanwadi",
        "time_to_climb": "2.5 - 3 hours",
        "water": "Sweet potable water available in cisterns near the cave throughout the year.",
        "night_stay": "Two natural rock caves on summit accommodate 25-30 people.",
        "difficulty": "Moderate (ladder sections on cliffs)",
        "source_url": "https://en.wikipedia.org/wiki/Ratangad",
        "highlights": "Nedhe (natural 'eye of the needle' rock cavity), Amruteshwar Temple"
    },
    {
        "fort_name": "Anjaneri",
        "district": "Nashik",
        "latitude": 19.92,
        "longitude": 73.57,
        "height_ft": 4264,
        "height": "4,264 ft (1,300 m)",
        "base_village": "Anjaneri village (near Trimbakeshwar)",
        "time_to_climb": "2 - 2.5 hours",
        "water": "Water ponds and natural springs on plateau; water stalls during peak season.",
        "night_stay": "Anjani Mata temple atop plateau can host 20 people; stay also in base village.",
        "difficulty": "Easy to Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Anjaneri",
        "highlights": "Birthplace of Lord Hanuman, rare wildflowers, Jain temple ruins"
    },
    {
        "fort_name": "Shivneri",
        "district": "Pune",
        "latitude": 19.199,
        "longitude": 73.8595,
        "height_ft": 3500,
        "height": "3,500 ft (1,067 m)",
        "base_village": "Junnar",
        "time_to_climb": "1 - 1.5 hours",
        "water": "Badami Talav, Ganga-Jamuna cisterns; bottled water available.",
        "night_stay": "Overnight stay on fort restricted by ASI; abundant lodging in Junnar town.",
        "difficulty": "Easy (well-maintained stone stairs through 7 gates)",
        "source_url": "https://en.wikipedia.org/wiki/Shivneri",
        "highlights": "Birthplace of Chhatrapati Shivaji Maharaj, Koli soldier memorial"
    },
    {
        "fort_name": "Kunjargad",
        "district": "Ahmednagar",
        "latitude": 19.392361,
        "longitude": 73.862,
        "height_ft": 3700,
        "height": "3,700 ft (1,128 m)",
        "base_village": "Kothale / Mulshet",
        "time_to_climb": "1.5 - 2 hours",
        "water": "Water cisterns on top; scarce in summer, carry water.",
        "night_stay": "Small cave accommodates 5-6 trekkers; homestay in Kothale village.",
        "difficulty": "Moderate",
        "source_url": "https://en.wikipedia.org/wiki/List_of_forts_in_Maharashtra",
        "highlights": "Panoramic views of Harishchandragad, Mandvi river valley"
    },
    {
        "fort_name": "Pabargad",
        "district": "Ahmednagar",
        "latitude": 19.482361,
        "longitude": 73.752833,
        "height_ft": 3800,
        "height": "3,800 ft (1,158 m)",
        "base_village": "Guhire",
        "time_to_climb": "2 - 2.5 hours",
        "water": "Water cisterns near rock steps; carry clean drinking water.",
        "night_stay": "Open camping on plateau or base village homestay in Guhire.",
        "difficulty": "Moderate",
        "source_url": "https://en.wikipedia.org/wiki/List_of_forts_in_Maharashtra",
        "highlights": "Offbeat fort overlooking Bhandardara waters and Kalsubai ridge"
    },
    {
        "fort_name": "Achala Fort",
        "district": "Nashik",
        "latitude": 20.431722,
        "longitude": 73.81525,
        "height_ft": 4050,
        "height": "4,050 ft (1,234 m)",
        "base_village": "Dagad Pimpri",
        "time_to_climb": "1.5 - 2 hours",
        "water": "Water tanks exist on fort but lack potable water; carry own water.",
        "night_stay": "Villagers in Dagad Pimpri base village provide warm meals and night stay.",
        "difficulty": "Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Achala_Fort",
        "highlights": "Twin sentinel with Ahivant in the Satmala range"
    },
    {
        "fort_name": "Ahivant Fort",
        "district": "Nashik",
        "latitude": 20.415444,
        "longitude": 73.86,
        "height_ft": 4035,
        "height": "4,035 ft (1,230 m)",
        "base_village": "Daregaon / Daregaonwani",
        "time_to_climb": "1.5 - 2 hours",
        "water": "Water cisterns on the expansive plateau; carry drinking water.",
        "night_stay": "Camping on the flat plateau or homestay in Daregaon base village.",
        "difficulty": "Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Ahivant_Fort",
        "highlights": "Massive natural flat plateau, historic triple gateway ruins"
    },
    {
        "fort_name": "Bhairavgad",
        "district": "Ahmednagar",
        "latitude": 19.3178131,
        "longitude": 73.7131545,
        "height_ft": 3750,
        "height": "3,750 ft (1,143 m)",
        "base_village": "Moroshi (Malshej Ghat)",
        "time_to_climb": "2.5 - 3 hours",
        "water": "Rock-cut water cisterns at top; carry sufficient drinking water.",
        "night_stay": "Rock-cut cave at the summit accommodates 10-15 trekkers.",
        "difficulty": "Thrilling (steep rock wall with carved steps)",
        "source_url": "https://en.wikipedia.org/wiki/Bhairavgad_(fort)",
        "highlights": "Spectacular needle pinnacle rising directly over Malshej Ghat"
    },
    {
        "fort_name": "Daulatabad Fort",
        "district": "Chhatrapati Sambhajinagar",
        "latitude": 19.942724,
        "longitude": 75.213164,
        "height_ft": 2750,
        "height": "2,750 ft (838 m)",
        "base_village": "Daulatabad",
        "time_to_climb": "1.5 - 2 hours",
        "water": "Bottled water and drinking facilities available all along the route.",
        "night_stay": "Monument closes at sunset; hotels in Chhatrapati Sambhajinagar city.",
        "difficulty": "Easy to Moderate (walk-in heritage fort with stairs)",
        "source_url": "https://en.wikipedia.org/wiki/Daulatabad_Fort",
        "highlights": "Impenetrable moat, Chand Minar, pitch-black Andhari maze passage"
    },
    {
        "fort_name": "Antur Fort",
        "district": "Chhatrapati Sambhajinagar",
        "latitude": 20.427345,
        "longitude": 75.236017,
        "height_ft": 2700,
        "height": "2,700 ft (823 m)",
        "base_village": "Nagapur (Kannad taluka)",
        "time_to_climb": "1 - 1.5 hours",
        "water": "Rock-cut water tanks near gates; carry drinking water.",
        "night_stay": "Dargah and shelter on fort accommodate small groups; village stay in Nagapur.",
        "difficulty": "Easy to Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Antur_Fort",
        "highlights": "Deep forest surrounding Gautala Wildlife Sanctuary"
    },
    {
        "fort_name": "Laling",
        "district": "Dhule",
        "latitude": 20.812,
        "longitude": 74.7395,
        "height_ft": 2050,
        "height": "2,050 ft (625 m)",
        "base_village": "Laling",
        "time_to_climb": "45 min - 1 hour",
        "water": "Cisterns near ruined palace; carry bottled water.",
        "night_stay": "Hemadpanthi temple at base or hotels in nearby Dhule city.",
        "difficulty": "Easy",
        "source_url": "https://en.wikipedia.org/wiki/Laling_fort",
        "highlights": "Faruqi dynasty stronghold commanding the Mumbai-Agra pass"
    },
    {
        "fort_name": "Bhamer",
        "district": "Dhule",
        "latitude": 21.07,
        "longitude": 74.33,
        "height_ft": 2400,
        "height": "2,400 ft (732 m)",
        "base_village": "Bhamer",
        "time_to_climb": "1 - 1.5 hours",
        "water": "Rock-cut caves have water cisterns; carry drinking water.",
        "night_stay": "More than 80 ancient rock-cut caves provide shelter for 25+ trekkers.",
        "difficulty": "Easy to Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Bhamer_Dhule",
        "highlights": "Remarkable cave complex and rock inscriptions"
    },
    {
        "fort_name": "Lohagad",
        "district": "Pune",
        "latitude": 18.70889,
        "longitude": 73.47667,
        "height_ft": 3389,
        "height": "3,389 ft (1,033 m)",
        "base_village": "Lohagadwadi (near Malavli / Lonavala)",
        "time_to_climb": "1 - 1.5 hours",
        "water": "Freshwater cisterns on the plateau; water stalls during weekends.",
        "night_stay": "South-side caves shelter small groups; villagers provide homestays and food.",
        "difficulty": "Easy (wide stone steps)",
        "source_url": "https://en.wikipedia.org/wiki/Lohagad",
        "highlights": "Vinchukata (scorpion tail) ridge, 4 monumental gates, monsoon mist"
    },
    {
        "fort_name": "Sinhagad",
        "district": "Pune",
        "latitude": 18.3656639,
        "longitude": 73.7552694,
        "height_ft": 4304,
        "height": "4,304 ft (1,312 m)",
        "base_village": "Donje / Atkarwadi",
        "time_to_climb": "1.5 - 2 hours (or drive up via road)",
        "water": "Famous 'Dev Taki' naturally cooled potable sweet water year-round.",
        "night_stay": "Overnight stay on top restricted; daytime huts serve pithla-bhakri.",
        "difficulty": "Easy to Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Sinhagad",
        "highlights": "Tanaji Malusare memorial, Kalyan Darwaja, Dev Taki spring"
    },
    {
        "fort_name": "Rajgad",
        "district": "Pune",
        "latitude": 18.2459862,
        "longitude": 73.6821929,
        "height_ft": 4514,
        "height": "4,514 ft (1,376 m)",
        "base_village": "Gunjavane / Pali",
        "time_to_climb": "2.5 - 3 hours",
        "water": "Padmavati tank and Sanjivani water cisterns provide good potable water.",
        "night_stay": "Padmavati temple accommodates 50+ trekkers comfortably.",
        "difficulty": "Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Rajgad",
        "highlights": "First capital of Maratha Empire for 26 years; Suvela & Sanjivani Machis"
    },
    {
        "fort_name": "Torna",
        "district": "Pune",
        "latitude": 18.2760722,
        "longitude": 73.6227167,
        "height_ft": 4603,
        "height": "4,603 ft (1,403 m)",
        "base_village": "Velhe",
        "time_to_climb": "3 - 3.5 hours",
        "water": "Water tanks near Menghai Devi temple and Budhla Machi; filter before use.",
        "night_stay": "Menghai Devi temple atop fort accommodates 25-30 trekkers.",
        "difficulty": "Moderate to Strenuous",
        "source_url": "https://en.wikipedia.org/wiki/Torna_Fort",
        "highlights": "First fort captured by Chhatrapati Shivaji Maharaj at age 16; Budhla Machi"
    },
    {
        "fort_name": "Raigad",
        "district": "Raigad",
        "latitude": 18.2335,
        "longitude": 73.4406,
        "height_ft": 2700,
        "height": "2,700 ft (820 m)",
        "base_village": "Pachad",
        "time_to_climb": "2 - 2.5 hours (or 5 minutes via Raigad Ropeway)",
        "water": "Ganga Sagar lake and potable water dispensers at summit.",
        "night_stay": "MTDC resort and guest cottages at summit provide comfortable rooms.",
        "difficulty": "Moderate (or Easy via Ropeway)",
        "source_url": "https://en.wikipedia.org/wiki/Raigad_fort",
        "highlights": "Capital of the Maratha Empire, Coronation throne site, Hirakani Buruj"
    },
    {
        "fort_name": "Pratapgad",
        "district": "Satara",
        "latitude": 17.936224,
        "longitude": 73.577607,
        "height_ft": 3556,
        "height": "3,556 ft (1,084 m)",
        "base_village": "Wada (near Mahabaleshwar)",
        "time_to_climb": "45 min - 1 hour (vehicle accessible to base gate)",
        "water": "Multiple potable water stalls and restaurants at base and top.",
        "night_stay": "Hotels and resorts in Mahabaleshwar (20 km) or base village homestays.",
        "difficulty": "Easy",
        "source_url": "https://en.wikipedia.org/wiki/Pratapgad",
        "highlights": "Site of historic encounter between Shivaji Maharaj and Afzal Khan, Bhavani Temple"
    },
    {
        "fort_name": "Panhala",
        "district": "Kolhapur",
        "latitude": 16.80889,
        "longitude": 74.10917,
        "height_ft": 2772,
        "height": "2,772 ft (845 m)",
        "base_village": "Panhala hill station",
        "time_to_climb": "Road access directly to fort; 1 hour walk",
        "water": "Municipal water and Sadhana tanks readily available.",
        "night_stay": "Numerous hill station hotels, MTDC resort, and homestays.",
        "difficulty": "Easy",
        "source_url": "https://en.wikipedia.org/wiki/Panhala_Fort",
        "highlights": "Sajja Kothi, Teen Darwaza, starting point of legendary Pawan Khind trek"
    },
    {
        "fort_name": "Vishalgad",
        "district": "Kolhapur",
        "latitude": 16.90611,
        "longitude": 73.74333,
        "height_ft": 3124,
        "height": "3,124 ft (952 m)",
        "base_village": "Gajapur",
        "time_to_climb": "1 - 1.5 hours",
        "water": "Wells and potable tanks near the dargah and temple.",
        "night_stay": "Dargah guesthouses and village homestays.",
        "difficulty": "Easy to Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Vishalgad",
        "highlights": "Historic terminus of Baji Prabhu Deshpande's Pawan Khind sacrifice"
    },
    {
        "fort_name": "Kharda",
        "district": "Ahmednagar",
        "latitude": 18.6331398,
        "longitude": 75.4747331,
        "height_ft": 2150,
        "height": "2,150 ft (655 m)",
        "base_village": "Kharda town",
        "time_to_climb": "30 minutes (plain land fortress)",
        "water": "Town amenities available; carry water bottles.",
        "night_stay": "Hotels and lodges in Kharda town or Jamkhed.",
        "difficulty": "Easy (walk-in ground fort)",
        "source_url": "https://en.wikipedia.org/wiki/Kharda",
        "highlights": "Shivpattana fort; site of historic 1795 Battle of Kharda against the Nizam"
    },
    {
        "fort_name": "Thalner",
        "district": "Dhule",
        "latitude": 21.255,
        "longitude": 74.955,
        "height_ft": 600,
        "height": "600 ft (183 m)",
        "base_village": "Thalner",
        "time_to_climb": "30 minutes",
        "water": "Village facilities available.",
        "night_stay": "Stay in Shirpur (15 km) or Dhule.",
        "difficulty": "Easy",
        "source_url": "https://en.wikipedia.org/wiki/Thalner",
        "highlights": "Ancient capital of the Faruqi kings situated on the banks of Tapi river"
    },
    {
        "fort_name": "Bhudargad",
        "district": "Kolhapur",
        "latitude": 16.235033,
        "longitude": 74.048109,
        "height_ft": 3200,
        "height": "3,200 ft (975 m)",
        "base_village": "Pushpanagar",
        "time_to_climb": "1 - 1.5 hours",
        "water": "Bhairavnath temple water tank.",
        "night_stay": "Bhairavnath temple hall accommodates 20 trekkers.",
        "difficulty": "Easy to Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Bhudargad",
        "highlights": "Scenic southern Maharashtra tableland fort"
    },
    {
        "fort_name": "Pargadh",
        "district": "Kolhapur",
        "latitude": 15.81649,
        "longitude": 74.04562,
        "height_ft": 2425,
        "height": "2,425 ft (739 m)",
        "base_village": "Malatwadi / Pargadh",
        "time_to_climb": "1.5 - 2 hours",
        "water": "Freshwater tanks and active village wells on top.",
        "night_stay": "Maruti temple on fort or homestays with warm local villagers.",
        "difficulty": "Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Pargadh",
        "highlights": "Border fortress with Goa surrounded by thick tropical jungle"
    },
    {
        "fort_name": "Akola Fort",
        "district": "Akola",
        "latitude": 20.706225,
        "longitude": 76.990019,
        "height_ft": 925,
        "height": "925 ft (282 m)",
        "base_village": "Akola city",
        "time_to_climb": "30 minutes (urban ground fort)",
        "water": "City amenities available.",
        "night_stay": "Hotels in Akola city.",
        "difficulty": "Easy",
        "source_url": "https://en.wikipedia.org/wiki/Akola_Fort",
        "highlights": "Asadgad fortress built on the Morna River"
    },
    {
        "fort_name": "Balapur",
        "district": "Akola",
        "latitude": 20.670309,
        "longitude": 76.7737,
        "height_ft": 950,
        "height": "950 ft (290 m)",
        "base_village": "Balapur town",
        "time_to_climb": "30 minutes",
        "water": "Town amenities available.",
        "night_stay": "Stay in Balapur or Akola city.",
        "difficulty": "Easy",
        "source_url": "https://en.wikipedia.org/wiki/Balapur_Fort",
        "highlights": "Mughal river confluence fortress and Chhatri of Mirza Raja Jai Singh"
    },
    {
        "fort_name": "Gawilghur",
        "district": "Amravati",
        "latitude": 21.38222,
        "longitude": 77.33389,
        "height_ft": 3590,
        "height": "3,590 ft (1,094 m)",
        "base_village": "Chikhaldara",
        "time_to_climb": "1 - 1.5 hours",
        "water": "Ancient water tanks on fort; carry drinking water.",
        "night_stay": "Hotels and resorts in Chikhaldara hill station.",
        "difficulty": "Easy to Moderate",
        "source_url": "https://en.wikipedia.org/wiki/Gawilghur",
        "highlights": "Site of Wellington's 1803 siege, Melghat tiger reserve views"
    },
    {
        "fort_name": "Ballarpur Fort",
        "district": "Chandrapur",
        "latitude": 19.8508361,
        "longitude": 79.341875,
        "height_ft": 700,
        "height": "700 ft (213 m)",
        "base_village": "Ballarpur",
        "time_to_climb": "30 minutes",
        "water": "Town amenities available.",
        "night_stay": "Hotels in Ballarpur or Chandrapur city.",
        "difficulty": "Easy",
        "source_url": "https://en.wikipedia.org/wiki/Ballarpur_Fort",
        "highlights": "Gond king Khandkya Ballal Sah heritage along Wardha River"
    },
    {
        "fort_name": "Manikgad",
        "district": "Chandrapur",
        "latitude": 19.675167,
        "longitude": 79.125417,
        "height_ft": 1660,
        "height": "1,660 ft (506 m)",
        "base_village": "Vihirgaon",
        "time_to_climb": "2 hours",
        "water": "Cisterns on fort; carry own drinking water.",
        "night_stay": "Wilderness camping; local guide recommended due to wildlife.",
        "difficulty": "Moderate (dense forest trail)",
        "source_url": "https://en.wikipedia.org/wiki/Manikgad",
        "highlights": "Ancient Gond hill fortress hidden within teak forests"
    },
    {
        "fort_name": "Udgir",
        "district": "Latur",
        "latitude": 18.4028,
        "longitude": 77.1178,
        "height_ft": 2070,
        "height": "2,070 ft (631 m)",
        "base_village": "Udgir town",
        "time_to_climb": "45 minutes",
        "water": "Tanks near samadhi; town facilities.",
        "night_stay": "Hotels in Udgir town.",
        "difficulty": "Easy",
        "source_url": "https://en.wikipedia.org/wiki/Udgir_Fort",
        "highlights": "Samadhi of Swami Udaygir, 1760 Battle of Udgir monument"
    },
    {
        "fort_name": "Bombay Castle",
        "district": "Mumbai City",
        "latitude": 18.931626,
        "longitude": 72.838143,
        "height_ft": 50,
        "height": "50 ft (15 m)",
        "base_village": "Fort, South Mumbai",
        "time_to_climb": "Walk-in heritage monument",
        "water": "City amenities available.",
        "night_stay": "Hotels in Mumbai.",
        "difficulty": "Easy (heritage walk)",
        "source_url": "https://en.wikipedia.org/wiki/Bombay_Castle",
        "highlights": "INS Angre naval compound, oldest British stone fort in Mumbai"
    },
    {
        "fort_name": "Dongri Fort",
        "district": "Mumbai City",
        "latitude": 19.3101833,
        "longitude": 72.7934472,
        "height_ft": 100,
        "height": "100 ft (30 m)",
        "base_village": "Dongri / Mira-Bhayandar",
        "time_to_climb": "20 minutes",
        "water": "Suburban amenities available.",
        "night_stay": "Hotels in Mumbai / Thane.",
        "difficulty": "Easy",
        "source_url": "https://en.wikipedia.org/wiki/Dongri_Fort",
        "highlights": "Dharavi Devi temple, coastal sea views over Vasai creek"
    },
    {
        "fort_name": "Ahmednagar Fort",
        "district": "Ahmednagar",
        "latitude": 19.0948,
        "longitude": 74.7480,
        "height_ft": 2130,
        "height": "2,130 ft (650 m)",
        "base_village": "Ahmednagar city",
        "time_to_climb": "30 minutes",
        "water": "City amenities available.",
        "night_stay": "Hotels in Ahmednagar city.",
        "difficulty": "Easy",
        "source_url": "https://en.wikipedia.org/wiki/Ahmednagar_Fort",
        "highlights": "Discovery of India written here by Nehru; historic 24 bastions"
    }
]

WIKIPEDIA_ATTRIBUTION = "Text and geographic data adapted from Wikipedia under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)."


def save_trek_cards():
    """Save the master trek data to data/trek_cards.json."""
    TREK_CARDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TREK_CARDS_FILE, "w", encoding="utf-8") as f:
        json.dump(TREK_DATA_MASTER, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(TREK_DATA_MASTER)} trek cards to {TREK_CARDS_FILE}")


def load_trek_cards():
    """Load trek cards from JSON file or master list."""
    if TREK_CARDS_FILE.exists():
        with open(TREK_CARDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return TREK_DATA_MASTER


def get_trek_cards_with_distance(town_name="Kopargaon", radius_km=None, min_height=None):
    """
    Get all trek cards with calculated distance from user's town.
    Filters by radius_km and min_height if provided.
    Sorted by distance (closest first).
    """
    towns = load_town_coordinates()
    town_key = town_name.strip().lower()

    if town_key not in towns:
        # Fallback to Kopargaon
        town_key = "kopargaon"

    ref_lat = towns[town_key]["latitude"]
    ref_lon = towns[town_key]["longitude"]

    cards = load_trek_cards()
    results = []

    for card in cards:
        lat = card.get("latitude")
        lon = card.get("longitude")
        if lat is None or lon is None:
            continue

        dist = haversine_distance(ref_lat, ref_lon, float(lat), float(lon))
        height_val = card.get("height_ft") or 0

        if min_height is not None and height_val < min_height:
            continue

        if radius_km is not None and dist > radius_km:
            continue

        card_copy = dict(card)
        card_copy["distance_km"] = round(dist, 1)
        card_copy["user_town"] = town_name.capitalize()
        card_copy["wikipedia_attribution"] = WIKIPEDIA_ATTRIBUTION
        results.append(card_copy)

    results.sort(key=lambda x: x["distance_km"])
    return results


def sync_records_with_trek_cards():
    """
    Sync heights, coordinates, base villages and trek notes into data/records.json.
    """
    if not RECORDS_FILE.exists():
        return

    with open(RECORDS_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    trek_lookup = {c["fort_name"].lower(): c for c in TREK_DATA_MASTER}

    updated_count = 0
    for record in records:
        name_key = record["fort_name"].lower()
        match = None
        for k, v in trek_lookup.items():
            if k == name_key or k in name_key or name_key in k:
                match = v
                break

        if match:
            if record.get("latitude") is None and match.get("latitude"):
                record["latitude"] = match["latitude"]
                record["longitude"] = match["longitude"]
            if record.get("height_ft") is None and match.get("height_ft"):
                record["height_ft"] = match["height_ft"]
            if not record.get("base_village") and match.get("base_village"):
                record["base_village"] = match["base_village"]
            if not record.get("trek_notes"):
                record["trek_notes"] = f"Climb: {match['time_to_climb']}. Water: {match['water']}. Stay: {match['night_stay']}."
            updated_count += 1

    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False)

    print(f"Synced {updated_count} records in {RECORDS_FILE}")


if __name__ == "__main__":
    save_trek_cards()
    sync_records_with_trek_cards()
