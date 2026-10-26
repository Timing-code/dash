import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Инициализация приложения
app = dash.Dash(__name__)
server = app.server # Необходимо для деплоя через gunicorn

# Загрузка данных
df = px.data.gapminder()

# Список числовых метрик для выбора
metrics = ['lifeExp', 'pop', 'gdpPercap']
metric_labels = {
    'lifeExp': 'Ожидаемая продолжительность жизни',
    'pop': 'Население',
    'gdpPercap': 'ВВП на душу населения'
}

# Формирование опций для дропдаунов
country_options = [{'label': country, 'value': country} for country in df['country'].unique()]
year_options = [{'label': str(year), 'value': year} for year in sorted(df['year'].unique())]
metric_options = [{'label': metric_labels[m], 'value': m} for m in metrics]

# Разметка дашборда (6 элементов управления, 4 графика)
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': '#f4f6f8'}, children=[
    html.H1("Глобальная статистика (Gapminder)", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    # --- Блок управления (6 элементов) ---
    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '15px', 'marginBottom': '20px', 'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
        
        # 1. Выбор нескольких стран
        html.Div(style={'flex': '1 1 300px'}, children=[
            html.Label("1. Выберите страны (мультивыбор):"),
            dcc.Dropdown(id='country-dropdown', options=country_options, value=['United States', 'China', 'India'], multi=True, clearable=True)
        ]),
        
        # 2. Выбор оси Y для линейного графика
        html.Div(style={'flex': '1 1 200px'}, children=[
            html.Label("2. Метрика для оси Y (Линейный график):"),
            dcc.Dropdown(id='y-axis-line-dropdown', options=metric_options, value='lifeExp', clearable=False)
        ]),
        
        # 3. Выбор оси X для пузырьковой диаграммы
        html.Div(style={'flex': '1 1 200px'}, children=[
            html.Label("3. Ось X (Пузырьковая диаграмма):"),
            dcc.Dropdown(id='bubble-x-dropdown', options=metric_options, value='gdpPercap', clearable=False)
        ]),
        
        # 4. Выбор оси Y для пузырьковой диаграммы
        html.Div(style={'flex': '1 1 200px'}, children=[
            html.Label("4. Ось Y (Пузырьковая диаграмма):"),
            dcc.Dropdown(id='bubble-y-dropdown', options=metric_options, value='lifeExp', clearable=False)
        ]),
        
        # 5. Выбор радиуса для пузырьковой диаграммы
        html.Div(style={'flex': '1 1 200px'}, children=[
            html.Label("5. Размер пузырьков (Мера):"),
            dcc.Dropdown(id='bubble-size-dropdown', options=metric_options, value='pop', clearable=False)
        ]),
        
        # 6. Выбор года (Кросс-фильтр для диаграмм 3, 4, 5)
        html.Div(style={'flex': '1 1 150px'}, children=[
            html.Label("6. Выберите год (Кросс-фильтр):"),
            dcc.Dropdown(id='year-dropdown', options=year_options, value=2007, clearable=False)
        ]),
    ]),

    # --- Блок визуализации (4 диаграммы) ---
    html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(500px, 1fr))', 'gap': '20px'}, children=[
        
        # График 1: Линейный график
        html.Div(style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
            html.H3("Динамика показателей по годам", style={'textAlign': 'center'}),
            dcc.Graph(id='line-chart')
        ]),
        
        # График 2: Пузырьковая диаграмма
        html.Div(style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
            html.H3("Пузырьковая диаграмма (по годам)", style={'textAlign': 'center'}),
            dcc.Graph(id='bubble-chart')
        ]),
        
        # График 3: Топ-15 стран по населению
        html.Div(style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
            html.H3("Топ-15 стран по населению", style={'textAlign': 'center'}),
            dcc.Graph(id='top15-chart')
        ]),
        
        # График 4: Круговая диаграмма по континентам
        html.Div(style={'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
            html.H3("Доля населения по континентам", style={'textAlign': 'center'}),
            dcc.Graph(id='pie-chart')
        ]),
    ])
])

# --- Callbacks (Логика обновления) ---

# 1. Обновление линейного графика
@app.callback(
    Output('line-chart', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('y-axis-line-dropdown', 'value')]
)
def update_line_chart(selected_countries, y_axis):
    if not selected_countries:
        return px.line(title="Выберите хотя бы одну страну")
    
    filtered_df = df[df['country'].isin(selected_countries)]
    fig = px.line(filtered_df, x='year', y=y_axis, color='country', 
                  title=f"Динамика: {metric_labels[y_axis]}",
                  labels={'year': 'Год', y_axis: metric_labels[y_axis]})
    fig.update_layout(hovermode="x unified")
    return fig

# 2. Обновление пузырьковой диаграммы (зависит от года)
@app.callback(
    Output('bubble-chart', 'figure'),
    [Input('bubble-x-dropdown', 'value'),
     Input('bubble-y-dropdown', 'value'),
     Input('bubble-size-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)
def update_bubble_chart(x_axis, y_axis, size_axis, selected_year):
    filtered_df = df[df['year'] == selected_year]
    fig = px.scatter(filtered_df, x=x_axis, y=y_axis, size=size_axis, color='continent',
                     hover_name='country', size_max=60,
                     title=f"Пузырьковая диаграмма за {selected_year} год",
                     labels={x_axis: metric_labels[x_axis], y_axis: metric_labels[y_axis]})
    fig.update_layout(legend_title_text='Континент')
    return fig

# 3. Обновление Топ-15 стран (зависит от года)
@app.callback(
    Output('top15-chart', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_top15_chart(selected_year):
    filtered_df = df[df['year'] == selected_year]
    # Сортировка по населению и выбор топ-15
    top15 = filtered_df.sort_values('pop', ascending=False).head(15)
    # Используем горизонтальный бар-чарт для лучшей читаемости названий стран
    fig = px.bar(top15, x='pop', y='country', color='continent', orientation='h',
                 title=f"Топ-15 стран по населению в {selected_year} году",
                 labels={'pop': 'Население', 'country': 'Страна'})
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

# 4. Обновление круговой диаграммы (зависит от года)
@app.callback(
    Output('pie-chart', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_pie_chart(selected_year):
    filtered_df = df[df['year'] == selected_year]
    # Группировка по континентам с суммированием населения
    grouped_df = filtered_df.groupby('continent')['pop'].sum().reset_index()
    fig = px.pie(grouped_df, values='pop', names='continent',
                 title=f"Распределение населения по континентам в {selected_year} году",
                 hole=0.3) # Делаем "пончик" для более современного вида
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)