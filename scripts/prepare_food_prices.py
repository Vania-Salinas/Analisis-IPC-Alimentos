import pandas as pd

# 1. Cargar datos raw 
# La base usa "\" como separador
input_path = "data/raw/base_anonimizada_ipc_2023.csv"

df = pd.read_csv(input_path, sep="\\", encoding="latin1")

print("✅ Datos cargados correctamente")
print(df.head())

# 2. Filtrar solo división Alimentos
# Según el diccionario IPC: 
# # DIVISION = 1 corresponde a Alimentos y bebidas no alcohólicas
df = df[df["DIVISION"] == 1]

# 3. Normalizar glosa a Title Case para visualización
df["Glosa_Producto"] = df["Glosa_Producto"].str.lower().str.title()

# 4. Seleccionar columnas de precios mensuales
# Solo precios promedio mensuales (pm_)
# Excluimos pm_16_ (levantamientos parciales)
price_columns = [
    col for col in df.columns
    if col.lower().startswith("pm_") and "16" not in col.lower()
]

columns_to_keep = ["Glosa_Producto"] + price_columns
df_prices = df[columns_to_keep]

# 5. Transformar a formato largo 
df_long = df_prices.melt(
    id_vars="Glosa_Producto",
    var_name="Periodo",
    value_name="Precio"
)

# 6. Limpiar nombres de periodo
df_long["Periodo"] = (
    df_long["Periodo"]
    .str.replace("pm_", "", regex=False)
    .str.replace("Pm_", "", regex=False)
)
# 7. Convertir periodo a fecha (meses en español)
meses = {
    "Enero": "01",
    "Febrero": "02",
    "Marzo": "03",
    "Abril": "04",
    "Mayo": "05",
    "Junio": "06",
    "Julio": "07",
    "Agosto": "08",
    "Septiembre": "09",
    "Octubre": "10",
    "Noviembre": "11",
    "Diciembre": "12"
}

def convertir_periodo_a_fecha(periodo):
    for mes, num in meses.items():
        if periodo.startswith(mes):
            year = periodo.replace(mes, "")
            return f"{year}-{num}-01"
    return None

df_long["Fecha"] = pd.to_datetime(
    df_long["Periodo"].apply(convertir_periodo_a_fecha),
    errors="coerce"
)

# 8. Eliminar precios nulos o cero
df_long = df_long.dropna(subset=["Fecha"])
df_long = df_long[df_long["Precio"] > 0]

# 9. Guardar dataset procesado
output_path = "data/processed/precios_alimentos_long.csv"
df_long.to_csv(output_path, index=False, encoding="utf-8")

print("Dataset procesado y listo para dashboard")
print(df_long.head())