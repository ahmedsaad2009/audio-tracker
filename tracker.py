import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- إعداد الصفحة ---
st.set_page_config(page_title="Audio Mastery Tracker", page_icon="🎧")
st.title("🎧 Audio Mastery Tracker")

# --- الاتصال بجوجل شيت ---
SHEET_NAME = "audio_data"

def get_data():
    # بنستخدم الـ Secrets للاتصال
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(credentials)
    
    try:
        sheet = client.open(SHEET_NAME).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return sheet, df
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None, None

# --- دالة تحويل الرقم لاسم المستوى ---
def get_level_label(score):
    if score >= 8:
        return "⭐⭐⭐ Proficient"
    elif score >= 5:
        return "⭐⭐ Competent"
    else:
        return "⭐ Novice"

# --- البرنامج ---
sheet, df = get_data()

if sheet is not None:
    if df.empty:
        df = pd.DataFrame(columns=["Audio Name", "Mastery Level", "Times Listened"])

    # --- الجزء العلوي: الإدخال ---
    st.subheader("What are you listening to?")
    option = st.radio("Choose Option:", ["Existing Audio", "New Audio"], horizontal=True)

    if option == "New Audio":
        new_name = st.text_input("Enter the name of the new audio:")
        if st.button("Add Audio"):
            if new_name and (df.empty or new_name not in df["Audio Name"].values):
                # إضافة صف جديد (الاسم، المستوى 0، عدد مرات الاستماع 0)
                new_row = [new_name, 0, 0]
                sheet.append_row(new_row)
                st.success(f"Added '{new_name}' successfully!")
                st.rerun()
            elif not df.empty and new_name in df["Audio Name"].values:
                st.warning("This audio already exists!")
            else:
                st.error("Please enter a name.")

    elif option == "Existing Audio":
        if not df.empty:
            audio_list = df["Audio Name"].tolist()
            selected_audio = st.selectbox("Select Audio:", audio_list)
            
            # استخراج البيانات الحالية
            row_idx = df[df["Audio Name"] == selected_audio].index[0]
            current_score = df.at[row_idx, "Mastery Level"]
            current_times = df.at[row_idx, "Times Listened"]
            
            # عرض المستوى الحالي بشكل شيك
            st.info(f"Current Level: {get_level_label(current_score)} ({current_score}/10)")
            
            if st.button("✅ I Listened to this now"):
                new_score = min(current_score + 1, 10)
                new_times = current_times + 1
                
                # تحديث جوجل شيت (رقم الصف الحقيقي = index + 2)
                real_row_num = row_idx + 2 
                sheet.update_cell(real_row_num, 2, new_score)      # العمود 2: Mastery Level
                sheet.update_cell(real_row_num, 3, new_times)      # العمود 3: Times Listened
                
                st.success(f"Updated! New Level: {get_level_label(new_score)}")
                st.balloons()
                st.rerun()
        else:
            st.info("No audio records yet.")

    st.markdown("---")
    
    # --- الجدول المعدل ---
    st.subheader("📊 Your Progress")
    if not df.empty:
        # 1. بنعمل نسخة للعرض عشان منغيرش البيانات الأصلية
        display_df = df.copy()
        
        # 2. بنحسب عمود جديد اسمه "Current Status" بناء على الأرقام
        display_df["Current Status"] = display_df["Mastery Level"].apply(get_level_label)
        
        # 3. بنعيد ترتيب الأعمدة (الاسم الأول، ثم مرات الاستماع، ثم الحالة)
        # لاحظ اننا شيلنا "Mastery Level" الرقمي وحطينا مكانه "Current Status" الكلام
        display_df = display_df[["Audio Name", "Times Listened", "Current Status"]]
        
        # عرض الجدول
        st.dataframe(display_df, use_container_width=True)
