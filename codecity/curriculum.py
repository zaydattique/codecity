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
("A decision in the greenhouse","A moisture sensor reads the soil. Python checks a condition and chooses one action. The plant responds to its environment over many simulated days."),
("Predict: dry soil","The sensor reads 20 percent. Our rule waters only below 40. Predict the valve action, then watch your choice and the correct rule."),
("Predict: moist soil","The sensor reads 60 percent. Does the same rule still turn water on? Predict, then compare your choice with the correct action."),
("Watch the correct rule","The controller checks moisture every simulated day. It opens the valve when the condition is true and closes it otherwise. Enough light and suitable temperature matter too."),
]
CODE_STEPS = [
("if moisture < 40:","The if statement compares moisture with 40. The colon starts an indented block."),
("    irrigate(True)","Only when the condition is true does Python run the indented action and open the valve."),
("else:","Else is the alternative. At exactly 40 the less-than comparison is false. Only one branch runs."),
("    irrigate(False)","The second indented block closes the valve. Change the sensor below to test both outcomes."),
]
CONCEPTS = [
("Less than / equality","< is strictly below; <= includes equality. == tests equality, not assignment. Try 39, 40 and 41 percent."),
("Indentation","Four spaces are the convention. Indentation groups the action with its branch. A missing block produces a Python syntax error."),
("elif","An elif is another condition checked only if earlier conditions are false. An else is the final fallback."),
("and","Both comparisons must be true. Python skips the second comparison if the first is false."),
("or","Either comparison can be true. In this example very dry soil or low moisture with adequate warmth permits watering."),
("not","not reverses a Boolean result. Here not moisture >= 40 has the same result as moisture < 40."),
]
EXAMPLES = [
"if moisture <= 40:\n    irrigate(True)\nelse:\n    irrigate(False)",
"if moisture < 40:\n    irrigate(True)\nelse:\n    irrigate(False)",
"if moisture < 30:\n    irrigate(True)\nelif moisture < 40:\n    irrigate(True)\nelse:\n    irrigate(False)",
"if moisture < 40 and temperature >= 12:\n    irrigate(True)\nelse:\n    irrigate(False)",
"if moisture < 20 or moisture < 40 and temperature >= 12:\n    irrigate(True)\nelse:\n    irrigate(False)",
"if not moisture >= 40:\n    irrigate(True)\nelse:\n    irrigate(False)",
]
