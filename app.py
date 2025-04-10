import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Configuración de la app
st.set_page_config(page_title="Anal-izador Bursátil Avanzado", layout="wide")
st.title("📈 Analizador Fundamental y de Riesgo")
st.text("Creado por Leonardo Aguilar Maraña")

# Sidebar para entrada de datos
with st.sidebar:
    st.header("Parámetros de Entrada")
    ticker = st.text_input("Ingrese el ticker bursátil (ej: AAPL, MSFT):", "").upper()
    st.markdown("""
    **Ejemplos válidos:**  
    - **Acciones:** AAPL (Apple), TSLA (Tesla)  
    - **ETFs:** SPY (S&P 500), QQQ (Nasdaq)  
    """)

# Función para validar y obtener datos
def get_ticker_data(ticker):
    if not ticker:
        return None, None
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        hist = ticker_obj.history(period="5y")
        
        if hist.empty or 'N/A' in str(info):
            st.error("Ticker inválido, por favor revise e intente de nuevo.")
            return None, None
        
        return info, hist
    except Exception:
        st.error("Ticker inválido, por favor revise e intente de nuevo.")
        return None, None

# Procesamiento principal
if ticker:
    info, hist = get_ticker_data(ticker)
    
    if info and not hist.empty:
        # --- Punto 1 y 2: Información Fundamental ---
        st.header("📋 Información Fundamental")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Datos Básicos")
            st.markdown(f"""
            - **Empresa:** {info.get('longName', 'N/A')}  
            - **Sector:** {info.get('sector', 'N/A')}  
            - **Industria:** {info.get('industry', 'N/A')}  
            """)
        
        with col2:
            st.subheader("Descripción")
            st.markdown(f"{info.get('longBusinessSummary', 'Descripción no disponible')}")
        
        # --- Punto 3: Gráfico de Precios Históricos (Plotly) ---
        st.header("📊 Precios Históricos (5 años)")
        fig = px.line(
            hist, x=hist.index, y="Close", 
            title=f"Evolución de {ticker}",
            labels={"Close": "Precio de Cierre (USD)", "index": "Fecha"}
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        
        # --- Punto 4: Cálculo de Rendimientos (CAGR) ---
        st.header("🧮 Rendimientos Anualizados (CAGR)")
        st.markdown("""
        **Fórmula del CAGR (Compound Annual Growth Rate):**  
        ```math
        CAGR = \left(\\frac{Precio\\ Final}{Precio\\ Inicial}\\right)^{\\frac{1}{Años}} - 1
        ```
        """)
        
        def calculate_cagr(start_price, end_price, years):
            return (end_price / start_price) ** (1/years) - 1
        
        cagr_1y = calculate_cagr(hist["Close"].iloc[-252], hist["Close"].iloc[-1], 1) if len(hist) >= 252 else np.nan
        cagr_3y = calculate_cagr(hist["Close"].iloc[-756], hist["Close"].iloc[-1], 3) if len(hist) >= 756 else np.nan
        cagr_5y = calculate_cagr(hist["Close"].iloc[0], hist["Close"].iloc[-1], 5)
        
        rendimientos_df = pd.DataFrame({
            "Período": ["1 año", "3 años", "5 años"],
            "CAGR": [f"{cagr_1y*100:.2f}%" if not np.isnan(cagr_1y) else "N/A", 
                    f"{cagr_3y*100:.2f}%" if not np.isnan(cagr_3y) else "N/A", 
                    f"{cagr_5y*100:.2f}%"]
        })
        st.table(rendimientos_df)
        
        # --- Punto 5: Cálculo del Riesgo (Volatilidad Anualizada) ---
        st.header("⚠️ Volatilidad Anualizada")
        returns = hist["Close"].pct_change().dropna()
        volatility = np.std(returns) * np.sqrt(252)
        
        st.markdown(f"""
        **Resultado:**  
        - **Volatilidad:** {volatility*100:.2f}%  
        - **Fórmula:** Desviación estándar de rendimientos diarios × √252  
        """)
        
        fig_hist = px.histogram(
            returns, 
            nbins=50,
            title="Distribución de Rendimientos Diarios",
            labels={"value": "Rendimiento Diario"}
        )
        fig_hist.add_vline(x=0, line_color="red")
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # --- Punto 6: Interfaz de Usuario Profesional ---
        st.markdown("---")
        st.header("🔍 Análisis Detallado")
        
        # --- Punto 7: Explicaciones Integradas ---
        with st.expander("📚 Explicaciones Técnicas"):
            st.markdown("""
            ### **Métricas Clave**  
            - **CAGR (Rendimiento Anualizado):**  
              Mide el crecimiento anual promedio de la inversión, asumiendo capitalización.  
              *Ejemplo: Si CAGR = 10%, \$100 se convertirían en \$161.05 en 5 años*.  
            
            - **Volatilidad:**  
              Indica la variabilidad de los rendimientos. Valores altos = mayor riesgo.  
              *Basada en la desviación estándar de los rendimientos diarios anualizada*.  
            
            ### **Fuente de Datos**  
            Datos históricos y fundamentales de **Yahoo Finance** (vía `yfinance`).  
            """)

else:
    st.warning("Por favor ingrese un ticker en el panel izquierdo.")
