import plotly.graph_objects as go
import plotly.express as px

# Данные из вашего графика
labels = ['BTC', 'ETH', 'SOL', 'USDT', 'USDC', 'DAI']
values = [59.3, 8.4, 2.2, 21.2, 8.3, 0.5]
categories = ['Нативные криптовалюты', 'Нативные криптовалюты', 'Нативные криптовалюты', 
              'Стейблкойны', 'Стейблкойны', 'Стейблкойны']

# Цвета: оранжевый для нативных криптовалют, зеленый для стейблкойнов
colors = ['#FF6B47', '#FF8A47', '#FFB347', '#4ECDC4', '#26A69A', '#00897B']
fig2 = go.Figure()

# Внутренний круг - категории (70% и 30%)
inner_labels = ['Нативные\nкриптовалюты', 'Стейблкойны']
inner_values = [70, 30]
inner_colors = ['#FF6B47', '#4ECDC4']

fig2.add_trace(go.Pie(
    labels=inner_labels,
    values=inner_values,
    domain=dict(x=[0.25, 0.75], y=[0.25, 0.75]),
    name="Категории",
    marker=dict(colors=inner_colors, line=dict(color='#FFFFFF', width=2)),
    textinfo='percent',
    textposition='inside',
    textfont=dict(size=32, color='white', family='Arial Black'),
    sort=False,
    showlegend=True,
    direction='clockwise',  # Направление: по часовой стрелке
    rotation=0
))

# Внешний круг - отдельные активы
fig2.add_trace(go.Pie(
    labels=[f'{label} {value}%' for label, value in zip(labels, values)],
    values=values,
    domain=dict(x=[0.1, 0.9], y=[0.1, 0.9]),
    name="Активы",
    marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)),
    showlegend=False,
    textinfo='label',
    textposition='outside',
    textfont=dict(size=16, color='#2C3E50'),
    hole=0.67,
    sort=False,
    direction='clockwise',  # Направление: по часовой стрелке
    rotation=0
))

fig2.update_layout(
    title={
        'text': '<b>Распределение криптопортфеля по классам активов</b><br>' +
                '<span style="font-size:14px;">Взвешивание по рыночной капитализации внутри класса</span>',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 16, 'color': '#2C3E50'}
    },
    font=dict(family="Arial, sans-serif", size=14, color="#2C3E50"),
    showlegend=True,
    width=900,
    height=700,
    paper_bgcolor='white',
    plot_bgcolor='white',
    margin=dict(l=100, r=100, t=100, b=50),
    annotations=[
        dict(
            text="Внешнее кольцо: Вес отдельных монет | Внутренний круг: Распределение по классам активов",
            showarrow=False,
            x=0.5,
            y=0,
            xref="paper",
            yref="paper",
            xanchor="center",
            yanchor="bottom",
            font=dict(size=14, color="#666666", family="Arial")
        )
    ]
)

fig2.update_layout(
    legend=dict(
        font=dict(size=14, color='#2C3E50'),
        x=0.5,        # положение по оси X (0 = слева, 1 = справа, 0.5 = центр)
        y=1.03,       # положение по оси Y (можно поднять/опустить)
        xanchor="center",  # якорь для выравнивания
        orientation="h"    # горизонтальное расположение
    )
)

# Save the figure as JPEG
fig2.write_image("portfolio_visualization_2025_Q2.png", format="png", width=900, height=700)

fig2.show()
