CATALOG_DATA = [
    {
        "category_name": "AC Service",
        "image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621765/yetzo_seed/ov9b9rgspyrbwmmmtbeh.jpg",
        "subcategories": [
            {
                "name": "Split AC",
                "services": [
                    {
                        "name": "Split AC Deep Clean",
                        "desc": "Advanced foam-jet cleaning for deep dust removal and better cooling.",
                        "price": {"Delhi NCR": 499, "Bangalore": 549, "Pune": 459, "Noida": 499, "Greater Noida": 499},
                        "duration": 45,
                        "variants": ["1 - 1.5 Ton", "2 Ton & Above"],
                        "addons": [("AC Gas Refill", 2500, 30), ("Anti-Rust Coating", 500, 15)],
                        "questions": [("How old is your AC?", ["0-2 Years", "3-5 Years", "5+ Years"])]
                    },
                    {
                        "name": "Split AC Repair",
                        "desc": "Thorough inspection and repair of your Split AC.",
                        "price": {"Delhi NCR": 299, "Bangalore": 349, "Pune": 259, "Noida": 299, "Greater Noida": 299},
                        "duration": 60,
                        "variants": ["Standard Visit"],
                        "addons": [("Capacitor Replacement", 400, 15), ("PCB Repair", 1500, 45)],
                        "questions": [("What is the issue?", ["Not cooling", "Making noise", "Water leaking", "Not turning on"])]
                    },
                    {
                        "name": "Split AC Installation",
                        "desc": "Complete installation of indoor and outdoor units with drilling.",
                        "price": {"Delhi NCR": 1199, "Bangalore": 1299, "Pune": 1099, "Noida": 1199, "Greater Noida": 1199},
                        "duration": 90,
                        "variants": ["1 - 1.5 Ton", "2 Ton & Above"],
                        "addons": [("Extra Copper Pipe (per m)", 300, 10), ("Wall Bracket", 450, 10)],
                        "questions": [("Is it a new AC?", ["Yes, brand new", "No, used"])]
                    }
                ]
            },
            {
                "name": "Window AC",
                "services": [
                    {
                        "name": "Window AC Deep Clean",
                        "desc": "Master cleaning of coils and fins with water jet.",
                        "price": {"Delhi NCR": 399, "Bangalore": 449, "Pune": 359, "Noida": 399, "Greater Noida": 399},
                        "duration": 45,
                        "variants": ["1 - 1.5 Ton", "2 Ton & Above"],
                        "addons": [("AC Gas Refill", 2500, 30)],
                        "questions": [("How old is your AC?", ["0-2 Years", "3-5 Years", "5+ Years"])]
                    },
                    {
                        "name": "Window AC Repair",
                        "desc": "Diagnosis and repair of Window AC cooling issues.",
                        "price": {"Delhi NCR": 299, "Bangalore": 349, "Pune": 259, "Noida": 299, "Greater Noida": 299},
                        "duration": 60,
                        "variants": ["Standard Visit"],
                        "addons": [("Fan Motor Repair", 1200, 45)],
                        "questions": [("What is the issue?", ["Not cooling", "Making noise", "Water leaking"])]
                    }
                ]
            }
        ]
    },
    {
        "category_name": "Cleaning",
        "image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621768/yetzo_seed/rkxfewrcu9h1j3yehu6a.jpg",
        "subcategories": [
            {
                "name": "Full Home Cleaning",
                "services": [
                    {
                        "name": "Intense Home Deep Cleaning",
                        "desc": "Mechanized deep cleaning of entire house, moving furniture, scrubbing floors.",
                        "price": {"Delhi NCR": 2999, "Bangalore": 3499, "Pune": 2599, "Noida": 2999, "Greater Noida": 2999},
                        "duration": 360,
                        "variants": ["1 BHK", "2 BHK", "3 BHK", "4 BHK", "Villa"],
                        "addons": [("Sofa Shampooing (per seat)", 200, 20), ("Fridge Deep Clean", 400, 30)],
                        "questions": [("Is your house furnished?", ["Fully Furnished", "Semi Furnished", "Empty"])]
                    },
                    {
                        "name": "Move-In/Move-Out Cleaning",
                        "desc": "Specialized cleaning for empty homes before moving in or after moving out.",
                        "price": {"Delhi NCR": 2499, "Bangalore": 2899, "Pune": 2299, "Noida": 2499, "Greater Noida": 2499},
                        "duration": 300,
                        "variants": ["1 BHK", "2 BHK", "3 BHK", "4 BHK"],
                        "addons": [("Balcony Pressure Wash", 300, 30)],
                        "questions": [("When are you moving?", ["Next 2 days", "Next week", "Just checking prices"])]
                    }
                ]
            },
            {
                "name": "Sofa & Carpet Cleaning",
                "services": [
                    {
                        "name": "Sofa Deep Cleaning",
                        "desc": "Dry vacuuming and wet shampooing of fabric sofas.",
                        "price": {"Delhi NCR": 499, "Bangalore": 599, "Pune": 449, "Noida": 499, "Greater Noida": 499},
                        "duration": 90,
                        "variants": ["3 Seater", "4 Seater", "5 Seater", "L-Shape"],
                        "addons": [("Carpet Shampooing (Small)", 300, 30), ("Cushion Cleaning (per pc)", 50, 5)],
                        "questions": [("What type of sofa?", ["Fabric", "Leather", "Suede"])]
                    }
                ]
            },
            {
                "name": "Bathroom & Kitchen Cleaning",
                "services": [
                    {
                        "name": "Bathroom Deep Cleaning",
                        "desc": "Removal of hard water stains, deep scrubbing of tiles and fixtures.",
                        "price": {"Delhi NCR": 399, "Bangalore": 449, "Pune": 359, "Noida": 399, "Greater Noida": 399},
                        "duration": 60,
                        "variants": ["1 Bathroom", "2 Bathrooms", "3 Bathrooms"],
                        "addons": [("Exhaust Fan Cleaning", 100, 15)],
                        "questions": [("Level of dirt/stains?", ["Regular", "Heavy Hard Water Stains"])]
                    },
                    {
                        "name": "Kitchen Deep Cleaning",
                        "desc": "Degreasing of chimneys, slabs, cabinets (exterior), and floor scrubbing.",
                        "price": {"Delhi NCR": 999, "Bangalore": 1199, "Pune": 899, "Noida": 999, "Greater Noida": 999},
                        "duration": 150,
                        "variants": ["Standard Kitchen", "Large Kitchen"],
                        "addons": [("Cabinet Interior Cleaning", 400, 45), ("Chimney Deep Clean", 600, 45)],
                        "questions": [("Are cabinets empty?", ["Yes", "No"])]
                    }
                ]
            }
        ]
    },
    {
        "category_name": "Maid Service",
        "image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621768/yetzo_seed/rkxfewrcu9h1j3yehu6a.jpg",
        "subcategories": [
            {
                "name": "Daily Maid Service",
                "services": [
                    {
                        "name": "Monthly Maid Booking (Sweeping/Moping)",
                        "desc": "Book a verified maid for daily sweeping and moping.",
                        "price": {"Delhi NCR": 1999, "Bangalore": 2499, "Pune": 1799, "Noida": 1999, "Greater Noida": 1999},
                        "duration": 60,
                        "variants": ["1 BHK", "2 BHK", "3 BHK"],
                        "addons": [("Dusting", 500, 15)],
                        "questions": [("Preferred Time?", ["Morning (7 AM - 11 AM)", "Afternoon", "Evening"])]
                    },
                    {
                        "name": "Monthly Maid (Cooking + Cleaning)",
                        "desc": "All rounder maid for 2 meals cooking plus sweeping, moping and utensils.",
                        "price": {"Delhi NCR": 5999, "Bangalore": 6999, "Pune": 4999, "Noida": 5999, "Greater Noida": 5999},
                        "duration": 180,
                        "variants": ["2 People", "4 People", "6+ People"],
                        "addons": [("Chapati Making only", 1000, 30)],
                        "questions": [("Diet Preference?", ["Vegetarian only", "Non-Vegetarian"])]
                    }
                ]
            },
            {
                "name": "On-Demand Helpers",
                "services": [
                    {
                        "name": "Party Helper / Server",
                        "desc": "Professional helper for serving food, managing kitchen during house parties.",
                        "price": {"Delhi NCR": 799, "Bangalore": 899, "Pune": 699, "Noida": 799, "Greater Noida": 799},
                        "duration": 240,
                        "variants": ["4 Hours", "6 Hours", "8 Hours"],
                        "addons": [("Bartender", 1200, 0)],
                        "questions": [("Expected Guest Count?", ["10-20", "20-50", "50+"])]
                    },
                    {
                        "name": "Utensils Cleaning (One-time)",
                        "desc": "Post-party or piled up utensils cleaning.",
                        "price": {"Delhi NCR": 299, "Bangalore": 349, "Pune": 249, "Noida": 299, "Greater Noida": 299},
                        "duration": 60,
                        "variants": ["Standard Sink Full", "Large Pile"],
                        "addons": [],
                        "questions": [("Are utensils scraped?", ["Yes", "No"])]
                    }
                ]
            }
        ]
    },
    {
        "category_name": "Plumbing",
        "image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621771/yetzo_seed/vmt5hhx4fra7ximexjb8.jpg",
        "subcategories": [
            {
                "name": "Tap & Sink",
                "services": [
                    {
                        "name": "Tap Repair / Replacement",
                        "desc": "Fixing leaking taps, replacing spindles or installing new taps.",
                        "price": {"Delhi NCR": 149, "Bangalore": 199, "Pune": 129, "Noida": 149, "Greater Noida": 149},
                        "duration": 30,
                        "variants": ["1 Tap", "2 Taps", "3 Taps"],
                        "addons": [("Provide new standard tap", 400, 0)],
                        "questions": [("Do you have the spare part?", ["Yes", "No, plumber should bring"])]
                    },
                    {
                        "name": "Wash Basin Repair",
                        "desc": "Fixing leaks, blockages or re-grouting the wash basin.",
                        "price": {"Delhi NCR": 249, "Bangalore": 299, "Pune": 199, "Noida": 249, "Greater Noida": 249},
                        "duration": 45,
                        "variants": ["Blockage Removal", "Leak Fix", "Complete Replacement"],
                        "addons": [("New Waste Pipe", 150, 0)],
                        "questions": [("What is the exact issue?", ["Blocked", "Leaking", "Broken"])]
                    }
                ]
            },
            {
                "name": "Toilet & Bath",
                "services": [
                    {
                        "name": "Toilet Blockage Removal",
                        "desc": "Professional unclogging of western or indian toilets.",
                        "price": {"Delhi NCR": 499, "Bangalore": 599, "Pune": 399, "Noida": 499, "Greater Noida": 499},
                        "duration": 60,
                        "variants": ["Minor Blockage", "Major Blockage (requires machine)"],
                        "addons": [],
                        "questions": [("Is water overflowing?", ["Yes", "No"])]
                    },
                    {
                        "name": "Flush Tank Repair",
                        "desc": "Fixing continuous water leak or non-working flush.",
                        "price": {"Delhi NCR": 199, "Bangalore": 249, "Pune": 149, "Noida": 199, "Greater Noida": 199},
                        "duration": 45,
                        "variants": ["Concealed Flush", "PVC Wall Flush", "Ceramic Flush"],
                        "addons": [("Syphon Set Replacement", 350, 0)],
                        "questions": []
                    }
                ]
            }
        ]
    },
    {
        "category_name": "Electrical",
        "image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621774/yetzo_seed/bw6kks9ztall5odyzrym.jpg",
        "subcategories": [
            {
                "name": "Fans & Lights",
                "services": [
                    {
                        "name": "Ceiling Fan Repair",
                        "desc": "Fixing slow speed, noise, or replacing capacitor/regulator.",
                        "price": {"Delhi NCR": 149, "Bangalore": 199, "Pune": 129, "Noida": 149, "Greater Noida": 149},
                        "duration": 30,
                        "variants": ["1 Fan", "2 Fans", "3 Fans"],
                        "addons": [("New Capacitor", 60, 0), ("New Regulator", 250, 0)],
                        "questions": [("What is the issue?", ["Not working", "Slow speed", "Making noise"])]
                    },
                    {
                        "name": "Light Installation",
                        "desc": "Installation of tube lights, fancy lights, or chandeliers.",
                        "price": {"Delhi NCR": 99, "Bangalore": 149, "Pune": 89, "Noida": 99, "Greater Noida": 99},
                        "duration": 30,
                        "variants": ["Basic Tube/LED", "Fancy Light", "Chandelier"],
                        "addons": [("Wiring Extension (per m)", 50, 10)],
                        "questions": [("Height of installation?", ["Normal (upto 10ft)", "High (Above 10ft)"])]
                    }
                ]
            },
            {
                "name": "Wiring & Switches",
                "services": [
                    {
                        "name": "Switchboard Repair",
                        "desc": "Fixing burnt switches, sockets, or installing new switchboards.",
                        "price": {"Delhi NCR": 149, "Bangalore": 199, "Pune": 129, "Noida": 149, "Greater Noida": 149},
                        "duration": 45,
                        "variants": ["1 Switchboard", "2 Switchboards", "Complete MCB Box"],
                        "addons": [("New 16A Socket", 150, 0)],
                        "questions": [("Is there a burning smell?", ["Yes", "No"])]
                    },
                    {
                        "name": "Inverter Installation",
                        "desc": "Complete setup of new inverter and battery with main line connection.",
                        "price": {"Delhi NCR": 499, "Bangalore": 599, "Pune": 399, "Noida": 499, "Greater Noida": 499},
                        "duration": 90,
                        "variants": ["Single Battery Setup", "Double Battery Setup"],
                        "addons": [("Provide Battery Trolley", 800, 0)],
                        "questions": [("Do you have the wiring ready?", ["Yes", "No"])]
                    }
                ]
            }
        ]
    },
    {
        "category_name": "Vehicle Repair",
        "image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621777/yetzo_seed/acq0ddffjr2ia1apgtjo.jpg",
        "subcategories": [
            {
                "name": "Two Wheeler Repair",
                "services": [
                    {
                        "name": "Bike/Scooty Comprehensive Service",
                        "desc": "Complete servicing including oil change, filter clean, chain lube and wash.",
                        "price": {"Delhi NCR": 499, "Bangalore": 599, "Pune": 399, "Noida": 499, "Greater Noida": 499},
                        "duration": 90,
                        "variants": ["Scooter/Scooty", "Commuter Bike (< 150cc)", "Sports Bike (> 150cc)"],
                        "addons": [("Engine Oil (Motul/Castrol)", 400, 0), ("Air Filter Change", 150, 0)],
                        "questions": [("When was the last service?", ["0-3 Months", "3-6 Months", "6+ Months"])]
                    },
                    {
                        "name": "Breakdown Assistance (Two Wheeler)",
                        "desc": "Mechanic at your location to fix start issue, puncture, or minor faults.",
                        "price": {"Delhi NCR": 299, "Bangalore": 349, "Pune": 249, "Noida": 299, "Greater Noida": 299},
                        "duration": 45,
                        "variants": ["Start Problem", "Puncture (Tubeless)", "Cable Break"],
                        "addons": [("New Spark Plug", 150, 0)],
                        "questions": [("Current situation?", ["At home", "Stranded on road"])]
                    }
                ]
            },
            {
                "name": "Car Repair & Service",
                "services": [
                    {
                        "name": "Car General Service",
                        "desc": "Engine oil change, oil filter, air filter cleaning, coolant top-up, 40 point check.",
                        "price": {"Delhi NCR": 1499, "Bangalore": 1699, "Pune": 1299, "Noida": 1499, "Greater Noida": 1499},
                        "duration": 180,
                        "variants": ["Hatchback", "Sedan", "SUV / MUV"],
                        "addons": [("Synthetic Engine Oil", 2500, 0), ("Wheel Alignment", 500, 30)],
                        "questions": [("Car fuel type?", ["Petrol", "Diesel", "CNG"])]
                    },
                    {
                        "name": "Car AC Repair & Gas Refill",
                        "desc": "AC inspection, leak test, condenser cleaning and R134a Gas refill.",
                        "price": {"Delhi NCR": 1999, "Bangalore": 2199, "Pune": 1799, "Noida": 1999, "Greater Noida": 1999},
                        "duration": 120,
                        "variants": ["Hatchback", "Sedan", "SUV / MUV"],
                        "addons": [("Cabin Filter Change", 350, 10)],
                        "questions": [("AC Cooling Status?", ["Low cooling", "No cooling at all", "Making noise"])]
                    }
                ]
            }
        ]
    },
    {
        "category_name": "Home Appliance Repair",
        "image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621777/yetzo_seed/acq0ddffjr2ia1apgtjo.jpg",
        "subcategories": [
            {
                "name": "Washing Machine",
                "services": [
                    {
                        "name": "Washing Machine Repair",
                        "desc": "Fixing issues like not spinning, water leakage, display errors or drum noise.",
                        "price": {"Delhi NCR": 299, "Bangalore": 349, "Pune": 249, "Noida": 299, "Greater Noida": 299},
                        "duration": 60,
                        "variants": ["Semi-Automatic", "Fully-Automatic Top Load", "Fully-Automatic Front Load"],
                        "addons": [("Descaling Powder", 200, 0), ("Inlet Pipe Replacement", 350, 10)],
                        "questions": [("What is the main issue?", ["Not draining", "Not spinning", "Making noise", "Dead/Not starting"])]
                    }
                ]
            },
            {
                "name": "Refrigerator",
                "services": [
                    {
                        "name": "Refrigerator Repair",
                        "desc": "Fixing cooling issues, compressor problems, or water leakage.",
                        "price": {"Delhi NCR": 299, "Bangalore": 349, "Pune": 249, "Noida": 299, "Greater Noida": 299},
                        "duration": 60,
                        "variants": ["Single Door", "Double Door", "Side-by-Side"],
                        "addons": [("Gas Refill (Single Door)", 1200, 45), ("Gas Refill (Double Door)", 1500, 45)],
                        "questions": [("What is the main issue?", ["Upper portion cooling, lower not", "No cooling", "Ice building up", "Making noise"])]
                    }
                ]
            },
            {
                "name": "Water Purifier (RO)",
                "services": [
                    {
                        "name": "RO Service & Repair",
                        "desc": "Filter change, membrane replacement, or fixing leaks/pump issues.",
                        "price": {"Delhi NCR": 299, "Bangalore": 349, "Pune": 249, "Noida": 299, "Greater Noida": 299},
                        "duration": 60,
                        "variants": ["General Service", "Repair Visit", "Installation"],
                        "addons": [("Complete Filter Kit", 1500, 30), ("RO Membrane", 1200, 30)],
                        "questions": [("When was it last serviced?", ["< 6 Months", "6-12 Months", "1+ Year"])]
                    }
                ]
            },
            {
                "name": "Geyser",
                "services": [
                    {
                        "name": "Geyser Repair & Service",
                        "desc": "Fixing no heating, water leakage, or auto cut-off failure.",
                        "price": {"Delhi NCR": 299, "Bangalore": 349, "Pune": 249, "Noida": 299, "Greater Noida": 299},
                        "duration": 60,
                        "variants": ["Instant Geyser (3-5L)", "Storage Geyser (10-25L)"],
                        "addons": [("Thermostat Replacement", 450, 20), ("Heating Element Replacement", 800, 30)],
                        "questions": [("What is the issue?", ["Not heating", "Shock coming", "Water leaking"])]
                    }
                ]
            }
        ]
    }
]
