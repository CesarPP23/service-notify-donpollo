import plotly.graph_objects as go
import pandas as pd
from utils.convertir_img_base64 import generar_imagen_base64
import logging

logger = logging.getLogger(__name__)

def _fmt_monto(v):
    try:
        return f"S/ {float(v):,.0f}"
    except Exception:
        return f"S/ {v}"

def _fmt_k(v):
    try:
        return f"S/ {float(v)/1000:,.1f}K"
    except Exception:
        return f"S/ {v}"

def generar_grafico_ventas_vs_presupuesto(df_combinado: pd.DataFrame) -> go.Figure:
    df = df_combinado.copy()

    # Asegurar tipos numéricos
    for c in ['ImporteProyectadoSemana', 'Ventas Totales (S/)', 'Cumplimiento']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    # Orden lógico por Año y Semana si existen
    if {'Año', 'Semana'}.issubset(df.columns):
        df = df.sort_values(['Año', 'Semana']).reset_index(drop=True)
        ticktext = [f"Sem. {sem}<br>{año}" for sem, año in zip(df['Semana'], df['Año'])]
    else:
        df = df.sort_values('Semana_Año').reset_index(drop=True)
        ticktext = df['Semana_Año'].astype(str).tolist()

    x_vals = df['Semana_Año']

    # Cálculos
    presupuesto_vals = df['ImporteProyectadoSemana']
    real_vals = df['Ventas Totales (S/)']

    # Faltante: cuánto le falta a Real para llegar a Presupuesto (solo positivo si hay déficit)
    faltante_altura = (presupuesto_vals - real_vals).clip(lower=0)  # 0 si no hay déficit
    faltante_base = real_vals  # arranca donde termina la barra Real

    # 1) Presupuestado (gris claro), grupo A
    presupuesto = go.Bar(
        x=x_vals,
        y=presupuesto_vals,
        name='Presupuestado',
        marker=dict(color="rgba(200, 200, 200, 0.6)", line=dict(width=0), cornerradius=8),
        width=0.4,
        text=presupuesto_vals.apply(_fmt_monto),
        textposition='inside',
        textfont=dict(color="#666", size=11),
        offsetgroup='A',
        hovertemplate='<b>Presupuesto</b><br>Semana: %{x}<br>Monto: %{text}<extra></extra>'
    )

    # 2) Real (gris oscuro), grupo B
    real = go.Bar(
        x=x_vals,
        y=real_vals,
        name='Real',
        marker=dict(color='rgb(128, 128, 128)', line=dict(width=0)),
        width=0.4,
        text=real_vals.apply(_fmt_k),
        textposition='inside',
        textfont=dict(color='black', size=11, family='Arial'),
        offsetgroup='B',
        hovertemplate='<b>Real</b><br>Semana: %{x}<br>Monto: %{text}<extra></extra>'
    )

    # 3) Faltante (franja roja), se dibuja sobre la barra Real (mismo grupo B)
    # Esto crea la “columna” roja que va desde el tope de Real hasta el monto de Presupuesto.
    faltante = go.Bar(
        x=x_vals,
        y=faltante_altura,
        base=faltante_base,
        name='',
        marker=dict(color="rgba(191, 48, 48, 0.4)", line=dict(width=0)),
        width=0.4,
        hoverinfo='skip',
        showlegend=False,
        offsetgroup='B'
    )

    fig = go.Figure()
    # En modo 'group', las barras A y B quedan lado a lado.
    # Dibujamos en este orden para que el rojo se vea por encima de la barra Real:
    fig.add_trace(presupuesto)  # izquierda (gris claro)
    fig.add_trace(real)         # derecha (gris oscuro)
    fig.add_trace(faltante)     # franja roja sobre barra real si falta

    # Anotaciones de Cumplimiento (1 decimal)
    for _, row in df.iterrows():
        c = pd.to_numeric(row.get('Cumplimiento'), errors='coerce')
        if pd.isna(c):
            continue
        c_txt = f"{float(c):.1f}%"
        if c < 100:
            # texto rojo sobre el presupuesto (muestra que está por debajo)
            fig.add_annotation(
                x=row['Semana_Año'],
                y=row['ImporteProyectadoSemana'],
                text=c_txt,
                showarrow=False,
                yshift=10,
                font=dict(color='red', size=12)
            )
        else:
            # texto verde sobre el real (logró o superó)
            fig.add_annotation(
                x=row['Semana_Año'],
                y=row['Ventas Totales (S/)'],
                text=c_txt,
                showarrow=False,
                yshift=10,
                font=dict(color='green', size=12)
            )

    # Layout final: barras lado a lado
    fig.update_layout(
        title=None,
        barmode='group',  # clave para verlas “al costado”
        xaxis=dict(
            tickvals=x_vals,
            ticktext=ticktext,
            tickangle=0,
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=14),
            tickformat="~s"
        ),
        plot_bgcolor="whitesmoke",
        paper_bgcolor="whitesmoke",
        legend=dict(
            font=dict(size=12),
            orientation="h",
            yanchor="middle",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=60, r=80, t=80, b=100)
    )

    return fig

def crear_imagen_ventas_semanales_vs_ppto(df: pd.DataFrame) -> str:
    figura = generar_grafico_ventas_vs_presupuesto(df)
    return generar_imagen_base64(figura)

def analizar_rendimiento(df_combinado: pd.DataFrame) -> dict:
    c = pd.to_numeric(df_combinado['Cumplimiento'], errors='coerce')
    return {
        'cumplimiento_promedio': c.mean(),
        'semanas_deficit': (c < 100).sum(),
        'semanas_superavit': (c > 100).sum(),
        'deficit_total': (100 - c.clip(upper=100)).sum(),
        'superavit_total': (c.clip(lower=100) - 100).sum()
    }