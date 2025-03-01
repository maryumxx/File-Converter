import streamlit as st
import pandas as pd
import os
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(page_title="Data Sweeper", layout="wide")

# Custom styling
st.markdown("""
    <style>
        .main {background-color: #121212;}
        .block-container {padding: 3rem 2rem; border-radius: 12px; background-color: #1e1e1e;}
        h1, h2, h3 {color: #66c2ff;}
        .stButton>button {border-radius: 8px; background-color: #0078D7; color: white; padding: 0.75rem 1.5rem;}
        .stButton>button:hover {background-color: #005a9e;}
        .stDownloadButton>button {background-color: #28a745; color: white;}
        .stDownloadButton>button:hover {background-color: #218838;}
    </style>
""", unsafe_allow_html=True)


st.write("Transform and clean your files with advanced features!")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx", "pdf"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()
        
        if file_extension == ".csv":
            df = pd.read_csv(file)
        elif file_extension == ".xlsx":
            excel_file = pd.ExcelFile(file)
            sheet = st.selectbox(f"Select a sheet from {file.name}", excel_file.sheet_names)
            df = pd.read_excel(excel_file, sheet_name=sheet)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            continue
        
        st.write(f"**📄 File Name:** {file.name} ({file.size / 1024:.2f} KB)")
        st.dataframe(df.head())
        
        # Data Summary
        st.subheader("📊 Data Summary")
        st.write(df.describe())
        
        # Column Data Type Conversion
        st.subheader("🔄 Convert Column Data Types")
        col_to_convert = st.selectbox("Select a column to convert", df.columns)
        dtype_choice = st.selectbox("Choose target data type", ["int", "float", "string", "datetime"])
        if st.button("Convert Data Type"):
            if dtype_choice == "int":
                df[col_to_convert] = pd.to_numeric(df[col_to_convert], errors='coerce').astype('Int64')
            elif dtype_choice == "float":
                df[col_to_convert] = pd.to_numeric(df[col_to_convert], errors='coerce')
            elif dtype_choice == "string":
                df[col_to_convert] = df[col_to_convert].astype(str)
            elif dtype_choice == "datetime":
                df[col_to_convert] = pd.to_datetime(df[col_to_convert], errors='coerce')
            st.write(f"Column `{col_to_convert}` converted to {dtype_choice}!")
        
        # Outlier Detection
        st.subheader("🚨 Outlier Detection")
        outlier_col = st.selectbox("Select a column to check for outliers", df.select_dtypes(include=[np.number]).columns)
        if st.button("Detect Outliers"):
            Q1, Q3 = df[outlier_col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
            outliers = df[(df[outlier_col] < lower) | (df[outlier_col] > upper)]
            st.write(f"Detected {len(outliers)} outliers in `{outlier_col}`")
            st.dataframe(outliers)
        
        # Advanced Visualization
        st.subheader("📈 Advanced Visualization")
        plot_type = st.selectbox("Select plot type", ["Histogram", "Box Plot", "Scatter Plot"])
        col1, col2 = st.selectbox("Select column for x-axis", df.columns), st.selectbox("Select column for y-axis", df.columns)
        if st.button("Generate Plot"):
            fig, ax = plt.subplots()
            if plot_type == "Histogram":
                sns.histplot(df[col1], bins=20, kde=True, ax=ax)
            elif plot_type == "Box Plot":
                sns.boxplot(x=df[col1], ax=ax)
            elif plot_type == "Scatter Plot":
                sns.scatterplot(x=df[col1], y=df[col2], ax=ax)
            st.pyplot(fig)
        
        # File Conversion and Download
        st.subheader("🔄 Convert & Download")
        conversion_type = st.radio("Convert file to:", ["CSV", "Excel"], key=file.name)
        new_file_name = st.text_input("Enter new file name (without extension)", file.name.split('.')[0])
        
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = f"{new_file_name}.csv"
                mime_type = "text/csv"
            else:
                df.to_excel(buffer, index=False, engine='openpyxl')
                file_name = f"{new_file_name}.xlsx"
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)
            st.download_button("⬇️ Download File", data=buffer, file_name=file_name, mime=mime_type)

st.success("🎉 All files processed successfully!")
