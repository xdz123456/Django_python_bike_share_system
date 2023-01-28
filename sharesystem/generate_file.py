old_file = open("../templates/sharesystem/new_map.html", "r")

lines = old_file.readlines()
new_file = open("../templates/sharesystem/template_map_cust.html", "w")

total = "{% extends 'sharesystem/MapCst.html' %}\n"

total += "{% block title_block %}\n"
for i in range(24, 40):
    total += lines[i]
total += "{% endblock %}\n"

total += "{% block body_block %}\n"

total += lines[44]

total += "{% endblock %}\n"

total += "{% block script_block %}\n"

for i in range(47, len(lines)):
    total += lines[i]

total += "\n{% endblock %}\n"


new_file.write(total)

old_file.close()
new_file.close()