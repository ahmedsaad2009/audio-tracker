import streamlit as st
import pandas as pd
import os

# 1. إعداد اسم الملف اللي هنحفظ فيه الداتا
DATA_FILE = 'audio_mastery.csv'

# 2. دالة لتحميل الداتا أو إنشاء ملف جديد لو مش موجود
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Audio Name", "Mastery Level", "Times Listened"])

# 3. دالة لحفظ الداتا
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- واجهة البرنامج ---
st.set_page_config(page_title="Audio Mastery Tracker", page_icon="🎧")

st.title("🎧 Audio Mastery Tracker")

# تحميل الداتا الحالية
df = load_data()

# اختيار الحالة: جديد ولا موجود؟
st.subheader("What are you listening to?")
option = st.radio("Choose Option:", ["Existing Audio", "New Audio"], horizontal=True)

if option == "New Audio":
    # لو ملف جديد
    new_name = st.text_input("Enter the name of the new audio:")
    if st.button("Add Audio"):
        if new_name and new_name not in df["Audio Name"].values:
            # إضافة صف جديد
            new_row = {"Audio Name": new_name, "Mastery Level": 0, "Times Listened": 0}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"Added '{new_name}' successfully!")
            st.rerun()
        elif new_name in df["Audio Name"].values:
            st.warning("This audio already exists!")
        else:
            st.error("Please enter a name.")

elif option == "Existing Audio":
    # لو ملف موجود
    if not df.empty:
        # قائمة منسدلة بالاوديو الموجود
        audio_list = df["Audio Name"].tolist()
        selected_audio = st.selectbox("Select Audio:", audio_list)
        
        # عرض المستوى الحالي
        current_level = df.loc[df["Audio Name"] == selected_audio, "Mastery Level"].values[0]
        st.info(f"Current Mastery Level: {current_level}/10")
        
        # زرار التسجيل
        if st.button("✅ I Listened to this now"):
            # تحديث الداتا
            # بنزود 1 بس ميزيدش عن 10
            new_level = min(current_level + 1, 10)
            
            df.loc[df["Audio Name"] == selected_audio, "Mastery Level"] = new_level
            df.loc[df["Audio Name"] == selected_audio, "Times Listened"] += 1
            save_data(df)
            
            st.success(f"Updated! New Level: {new_level}/10")
            st.balloons() # تأثير بصري لطيف
            
    else:
        st.write("No audio records yet. Add a 'New Audio' first.")

st.markdown("---")
# 4. عرض الجدول بالكامل عشان تشوف مستواك
st.subheader("📊 Your Progress")
if not df.empty:
    # عرض الجدول بشكل تفاعلي
    st.dataframe(
        df.style.background_gradient(subset=['Mastery Level'], cmap='Greens', vmin=0, vmax=10),
        use_container_width=True
    )
else:
    st.write("Start adding audios to see your stats here.")