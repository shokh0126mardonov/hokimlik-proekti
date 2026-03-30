import pandas as pd


def read_excel_and_print(file_path: str):
    # 1. Excelni o‘qish
    df = pd.read_excel(file_path)

    # 2. Columnlarni normalize qilish (agar header to‘g‘ri bo‘lmasa qo‘lda override qilamiz)
    df.columns = ["id", "mahalla", "full_name", "phone"]

    # 3. "sektor" row’larni olib tashlash
    df = df[~df["mahalla"].astype(str).str.contains("sektor", case=False, na=False)]

    # 4. Bo‘sh qiymatlarni olib tashlash
    df = df.dropna(subset=["mahalla", "full_name", "phone"])

    # 5. Telefonni tozalash (faqat raqamlar qoldiramiz)
    df["phone"] = (
        df["phone"]
        .astype(str)
        .str.replace(r"\D", "", regex=True)
    )

    # 6. Har bir qatorni chiqarish (optimal usul)
    for row in df.itertuples(index=False):
        print(
            f"Mahalla: {row.mahalla} | "
            f"F.I.SH: {row.full_name} | "
            f"Telefon: {row.phone}"
        )


if __name__ == "__main__":
    read_excel_and_print("Маҳалла раислари рўйхати.xlsx")