from dash import html, dcc

def footer(**kwargs):
    return html.Footer(
        id="footer", 
        className='fixed-bottom', 
        children=[
            "This is the footer, will format later"
        ]
    )