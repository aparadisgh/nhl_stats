from dash import html

layout = html.Div(
    id='app-container',
    className='container-xl',
    children=[
        html.Iframe(src='https://www.rotowire.com/hockey/starting-goalies.php?view=teams',
            style={"height": "1067px", "width": "100%"})
    ]
)