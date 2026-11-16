import io
import zipfile
from PIL import Image
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

# إعدادات الصفحة
st.set_page_config(
    page_title="أداة قص الصور الذكية", page_icon="✂️", layout="wide"
)

st.title(
    "✂️ أداة قص الصور الجماعية (مع ميزة تحديد البكسل بالضغط المباشر 🖱️)"
)
st.write(
    "ارفع صورك، اضغط على أي نقطة في الصورة لمعرفة إحداثياتها بالبكسل بدقة،"
    " وحدد أبعاد القص بناءً عليها!"
)

# رفع الصور متعددة
uploaded_files = st.file_uploader(
    "اختر الصور (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
)

if uploaded_files:
  st.success(f"تم رفع {len(uploaded_files)} صورة بنجاح! 🎉")

  # قراءة الصورة الأولى لأخذ الأبعاد المرجعية
  first_image = Image.open(uploaded_files[0])
  width, height = first_image.size

  st.info(
      f"📐 المقاس المرجعي للصورة الأولى: **{width} × {height} بكسل**. سيتم توحيد"
      " بقية الصور على هذا المقاس تلقائياً."
  )

  # قسم خاص بالضغط المباشر لمعرفة الإحداثيات
  st.markdown("---")
  st.subheader(
      "🎯 خريطة البكسل: اضغط على أي مكان في الصورة أدناه لمعرفة إحداثياته"
      " (X, Y)"
  )

  # عرض الصورة مع إمكانية التقاط مكان الضغط
  coords = streamlit_image_coordinates(first_image, key="click_coords")

  if coords is not None:
    clicked_x = coords["x"]
    clicked_y = coords["y"]
    st.success(
        f"📍 النقطة التي ضغطت عليها إحداثياتها: **X = {clicked_x}**, **Y ="
        f" {clicked_y}** بكسل"
    )
  else:
    st.info(
        "💡 نصيحة: اضغط بالماوس على أي حرف، أو شريط، أو أداة في الصورة بالأعلى"
        " لتعرف إحداثياتها بدقة."
    )

  st.markdown("---")

  # لوحة التحكم الجانبية للقص
  st.sidebar.header("⚙️ إعدادات القص (بالبكسل)")
  st.sidebar.write(
      "استخدم الإحداثيات اللي ظهرتلك فوق لضبط هوامش القص بدقة تامة:"
  )

  crop_top = st.sidebar.slider(
      "قص من الأعلى (Top)", 0, height // 2, 0, step=5
  )
  crop_bottom = st.sidebar.slider(
      "قص من الأسفل (Bottom)", 0, height // 2, 0, step=5
  )
  crop_left = st.sidebar.slider("قص من اليسار (Left)", 0, width // 2, 0, step=5)
  crop_right = st.sidebar.slider(
      "قص من اليمين (Right)", 0, width // 2, 0, step=5
  )

  # حساب إحداثيات القص
  left_box = crop_left
  upper_box = crop_top
  right_box = width - crop_right
  lower_box = height - crop_bottom

  # التحقق من صحة الأبعاد
  if left_box < right_box and upper_box < lower_box:
    # معاينة القص على الصورة الأولى
    st.subheader("👁️ معاينة القص النهائية على أول صورة")
    preview_img = first_image.crop((left_box, upper_box, right_box, lower_box))

    col1, col2 = st.columns(2)
    with col1:
      st.image(
          first_image, caption="الصورة الأصلية", use_container_width=True
      )
    with col2:
      st.image(preview_img, caption="الصورة بعد القص", use_container_width=True)

    st.markdown("---")

    # زر بدء المعالجة والتنزيل
    if st.button(
        "🚀 توحيد المقاسات وقص كل الصور دفعة واحدة",
        type="primary",
        use_container_width=True,
    ):
      zip_buffer = io.BytesIO()

      with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for idx, uploaded_file in enumerate(uploaded_files):
          img = Image.open(uploaded_file)

          # 1. توحيد المقاس بناءً على الصورة الأولى
          img_resized = img.resize((width, height), Image.Resampling.LANCZOS)

          # 2. تنفيذ القص
          cropped = img_resized.crop(
              (left_box, upper_box, right_box, lower_box)
          )

          # حفظ في الذاكرة المؤقتة
          img_byte_arr = io.BytesIO()
          img_format = img.format if img.format in ["PNG", "JPEG"] else "PNG"
          cropped.save(img_byte_arr, format=img_format)
          img_byte_arr.seek(0)

          # تسمية الملف داخل ملف الـ ZIP
          file_name = f"processed_{idx+1}_{uploaded_file.name}"
          zip_file.writestr(file_name, img_byte_arr.read())

      zip_buffer.seek(0)
      st.success(
          "✨ تم توحيد مقاسات الصور وقصها بنجاح وأصبحت جاهزة للتحميل!"
      )

      # زر التنزيل للكل
      st.download_button(
          label="📥 تحميل جميع الصور المعالجة (ZIP)",
          data=zip_buffer,
          file_name="processed_images.zip",
          mime="application/zip",
          use_container_width=True,
      )
  else:
    st.error(
        "⚠️ خطأ: إعدادات القص أكبر من أبعاد الصورة، يرجى تعديل المؤشرات."
    )
else:
  st.info("📂 الرجاء رفع مجموعة الصور للبدء.")
