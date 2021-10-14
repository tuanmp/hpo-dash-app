from dash import html, dcc

def footer(**kwargs):
    return html.Footer(
        id="footer", 
        className='page-footer', 
        children=[
            "This is the footer, will format later"
        ]
    )