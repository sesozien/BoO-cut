import io
import zipfile
from PIL import Image
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="أداة قص الصور الجماعية", page_icon="✂️", layout="wide"
)

st.title("✂️ أداة قص الصور الجماعية (Batch Image Cropper)")
st.write(
    "ارفع مجموعة صور، حدد أبعاد القص من الهوامش، وسيتم تطبيقها على كل الصور دفعة"
    " واحدة مع زر لتنزيلها جميعاً بملف واحد."
)

# رفع الصور متعددة
uploaded_files = st.file_uploader(
    "اختر الصور (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
)

if uploaded_files:
  st.success(f"تم رفع {len(uploaded_files)} صورة بنجاح! 🎉")

  # قراءة الصورة الأولى لأخذ الأبعاد ومعاينتها
  first_image = Image.open(uploaded_files[0])
  width, height = first_image.size

  st.info(
      f"📐 أبعاد الصورة الأولى: **{width} × {height} بكسل**. (يُفضل أن تكون باقي"
      " الصور قريبة من هذه الأبعاد لتجانس القص)."
  )

  # لوحة التحكم الجانبية للقص
  st.sidebar.header("⚙️ إعدادات القص (بالبكسل)")
  st.sidebar.write("حدد الهوامش المراد قصها من أطراف الصور:")

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
    st.subheader("👁️ معاينة القص على أول صورة")
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
        "🚀 معالجة وقص كل الصور دفعة واحدة",
        type="primary",
        use_container_width=True,
    ):
      zip_buffer = io.BytesIO()

      with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for idx, uploaded_file in enumerate(uploaded_files):
          img = Image.open(uploaded_file)
          w, h = img.size

          # ضبط القيم لكل صورة بحسب أبعادها لتجنب الأخطاء
          l = min(crop_left, w // 2)
          t = min(crop_top, h // 2)
          r = max(w - crop_right, l + 10)
          b = max(h - crop_bottom, t + 10)

          # تنفيذ القص
          cropped = img.crop((l, t, r, b))

          # حفظ الصورة في الذاكرة المؤقتة
          img_byte_arr = io.BytesIO()
          img_format = img.format if img.format in ["PNG", "JPEG"] else "PNG"
          cropped.save(img_byte_arr, format=img_format)
          img_byte_arr.seek(0)

          # تسمية الملف داخل ملف الـ ZIP
          file_name = f"cropped_{idx+1}_{uploaded_file.name}"
          zip_file.writestr(file_name, img_byte_arr.read())

      zip_buffer.seek(0)
      st.success("✨ تم قص جميع الصور بنجاح جاهزة للتحميل!")

      # زر التنزيل للكل
      st.download_button(
          label="📥 تحميل جميع الصور القصيرة (ZIP)",
          data=zip_buffer,
          file_name="cropped_images.zip",
          mime="application/zip",
          use_container_width=True,
      )
  else:
    st.error(
        "⚠️ خطأ: إعدادات القص التي أدخلتها أكبر من أبعاد الصورة الفعلية، يرجى"
        " تعديل المؤشرات."
    )
else:
  st.info("📂 الرجاء رفع مجموعة الصور التي ترغب في قصها للبدء.")
