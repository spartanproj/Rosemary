import markdown

with open('../README.md', 'r') as f:
    text = f.read()
    html = markdown.markdown(text,extensions=['fenced_code', 'codehilite','md_in_html'])

with open('index.html', 'w') as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rosemary</title>
    <link rel="stylesheet" href="static/css/codehilite.css"/>
</head>
<style>
    body {
        background:black;
        color:white;
        font-family:monospace
    }
    .codehilite {
        border-radius:7px
    }
    code:not(pre *){
        background:white;
        border-radius:3px;
        color:black
    }
</style>
<body>
</body>
</html>""")
    f.write(html)
