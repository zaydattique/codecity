"""BloomLogic curriculum. Only the greenhouse exhibit is currently interactive."""
LESSONS = [
("Print & Comments","Airport information board","Display flight messages; separate instructions from notes."),
("Variables","Smart warehouse","Update stock quantities in labeled storage bins."),
("Data Types","Grocery checkout","Scan price, product name, quantity and availability."),
("Operators","Solar energy station","Calculate energy production, cost and remainder."),
("If / Else","Greenhouse controller","Let Python decide when a plant receives water."),
("For Loops + range","Bottling line","Fill a fixed number of bottles one at a time."),
("Break & Continue","Quality inspection","Skip damaged items and stop at a critical fault."),
("Lists","Restaurant order rail","Add, remove and reorder live meal tickets."),
("Tuples","Surveyor's workshop","Store fixed coordinates of survey points."),
("Sets","Recycling center","Sort unique materials and remove duplicates."),
("Dictionaries","Parcel dispatch","Match parcel IDs with destinations and delivery status."),
("While Loops","Water treatment tank","Repeat pumping until a sensor reaches its target."),
("Functions","Coffee workstation","Reuse one recipe with different serving sizes."),
("String Methods","Library catalog","Clean, format and search book titles."),
]
GUIDE = [
("A decision in the greenhouse","This seed needs enough moisture to germinate. A sensor measures soil moisture. Python can decide whether to turn the irrigation valve on or off."),
("Predict the outcome","If the sensor reads 20 percent and our threshold is 40, should irrigation start? Think about whether 20 is less than 40."),
("Two possible branches","The if condition is true when moisture is below 40. Python runs the indented irrigation action. Otherwise the else branch turns the water off."),
]
CODE_STEPS = [
("if moisture < 40:","Python compares the live sensor reading with 40. The colon begins an indented block."),
("    irrigate(True)","When the condition is true, run this function and open the valve."),
("else:","When the condition is false, Python enters the alternative branch. At exactly 40, the condition is false."),
("    irrigate(False)","The indented else action closes the valve. Only one branch executes per check."),
]
