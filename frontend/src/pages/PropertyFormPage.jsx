import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createProperty } from "../api/properties";


// لیست‌های استاندارد برای Dropdownها
const provinceOptions = ["خراسان رضوی", "تهران", "مازندران", "اصفهان", "فارس"];
const cityOptions = {
  "خراسان رضوی": ["مشهد", "نیشابور", "سبزوار"],
  "تهران": ["تهران", "ورامین", "شهریار"],
};
const directionOptions = [
  { value: "NORTH", label: "شمالی" },
  { value: "SOUTH", label: "جنوبی" },
  { value: "EAST", label: "شرقی" },
  { value: "WEST", label: "غربی" },
  { value: "DOUBLESIDED", label: "دو کله" },
  { value: "NABSH", label: "نبش" },
];


const paymentTermsOptions = [
  { value: "CASH", label: "نقدی" },
  { value: "EXCHANGE", label: "معاوضه" },
  { value: "AGREEMENT", label: "توافقی" },
  { value: "INSTALLMENT", label: "اقساطی" },
];

const baseInitialState = {
  code: "", 
  title: "",
  transaction_type: "SALE",
  property_kind: "APARTMENT",
  other_kind_name: "", // برای فیلد سایر
  status: "ACTIVE",
  province: "خراسان رضوی",
  city: "مشهد",
  district: "",
  full_address: "",
  postal_code: "", // جدید
  map_link: "",
  area_sqm: "",
  land_area_sqm: "",
  bedrooms: "0",
  build_year: "",
  direction: "شمالی", // تبدیل به انتخابی
  document_type: "SINGLE_PAGE",
  // امکانات به صورت آرایه برای مدیریت راحت‌تر چک‌باکس‌ها
  amenities_list: [], 
  other_amenities: "",
  has_elevator: false,
  parking_count: "0",
  has_storage: false,
  has_balcony: false,
  is_renovated: false,
  owner_name: "",
  owner_phone: "",
  is_exclusive: false,
  public_description: "",
  private_note: "",
};

const transactionTypeOptions = [
  { value: "SALE", label: "فروش" },
  { value: "PRESALE", label: "پیش فروش" },
  { value: "RENT", label: "اجاره" },
  { value: "MORTGAGE", label: "رهن کامل" },
];

const propertyKindOptions = [
  { value: "APARTMENT", label: "آپارتمان" },
  { value: "VILLA", label: "ویلا" },
  { value: "OFFICE", label: "اداری" },
  { value: "COMMERCIAL", label: "تجاری" },
  { value: "LAND", label: "زمین" },
  { value: "OTHER", label: "سایر" },
];

const statusOptions = [
  { value: "ACTIVE", label: "فعال" },
  { value: "RESERVED", label: "رزرو" },
  { value: "CLOSED", label: "بسته شده" },
  { value: "INACTIVE", label: "غیرفعال" },
];

const documentTypeOptions = [
  { value: "SINGLE_PAGE", label: "تک برگ" },
  { value: "TASSELED", label: "منگوله دار" },
  { value: "AGREEMENT", label: "قولنامه ای" },
  { value: "OTHER", label: "سایر" },
];


const renewalStatusOptions = [
  { value: "NOT_CHECKED", label: "بررسی نشده" },
  { value: "WANTS_RENEWAL", label: "مایل به تمدید" },
  { value: "WANTS_TO_LEAVE", label: "مایل به تخلیه" },
  { value: "UNCLEAR", label: "نامشخص" },
  { value: "RENEWED", label: "تمدید شده" },
];

  
const detailInitialState = {
  SALE: {
    total_price: "",
    price_per_sqm: "",
    payment_terms: "CASH",
    down_payment: "",
    is_exchangeable: false,
  },
  PRESALE: {
    total_contract_price: "",
    builder_company: "",
    progress_percent: "",
    estimated_delivery_date: "",
    amount_paid: "",
    amount_remaining: "",
    installment_terms: "",
    contract_number: "",
  },
  RENT: {
    contract_start_date: "",
    contract_end_date: "",
    current_tenant_name: "",
    current_tenant_phone: "",
    renewal_status: "NOT_CHECKED",
    last_contact_result: "",
    next_contact_date: "",
    deposit_amount: "",
    monthly_rent: "",
    convertible_to_mortgage: false,
    yearly_increase_percent: "",
  },
  MORTGAGE: {
    contract_start_date: "",
    contract_end_date: "",
    current_tenant_name: "",
    current_tenant_phone: "",
    renewal_status: "NOT_CHECKED",
    last_contact_result: "",
    next_contact_date: "",
    deposit_amount: "",
  },
};

function toNullableNumber(value) {
  if (value === "" || value === null || value === undefined) return null;
  const parsed = Number(value);
  return Number.isNaN(parsed) ? null : parsed;
}

function cleanObject(obj) {
  const entries = Object.entries(obj).filter(([, value]) => value !== undefined);
  return Object.fromEntries(entries);
}

function buildPayload(form, detailMap) {
  const payload = {
    ...form,
    area_sqm: toNullableNumber(form.area_sqm),
    land_area_sqm: toNullableNumber(form.land_area_sqm),
    bedrooms: toNullableNumber(form.bedrooms),
    build_year: toNullableNumber(form.build_year),
    total_floors: toNullableNumber(form.total_floors),
    unit_floor: toNullableNumber(form.unit_floor),
    units_per_floor: toNullableNumber(form.units_per_floor),
    parking_count: toNullableNumber(form.parking_count),
    detail: {},
  };

  const rawDetail = detailMap[form.transaction_type];

  if (form.transaction_type === "SALE") {
    payload.detail = cleanObject({
      total_price: toNullableNumber(rawDetail.total_price),
      price_per_sqm: toNullableNumber(rawDetail.price_per_sqm),
      payment_terms: rawDetail.payment_terms,
      down_payment: toNullableNumber(rawDetail.down_payment),
      is_exchangeable: rawDetail.is_exchangeable,
    });
  }

  if (form.transaction_type === "PRESALE") {
    payload.detail = cleanObject({
      total_contract_price: toNullableNumber(rawDetail.total_contract_price),
      builder_company: rawDetail.builder_company || "",
      progress_percent: toNullableNumber(rawDetail.progress_percent),
      estimated_delivery_date: rawDetail.estimated_delivery_date || null,
      amount_paid: toNullableNumber(rawDetail.amount_paid),
      amount_remaining: toNullableNumber(rawDetail.amount_remaining),
      installment_terms: rawDetail.installment_terms || "",
      contract_number: rawDetail.contract_number || "",
    });
  }

  if (form.transaction_type === "RENT") {
    payload.detail = cleanObject({
      contract_start_date: rawDetail.contract_start_date || null,
      contract_end_date: rawDetail.contract_end_date || null,
      current_tenant_name: rawDetail.current_tenant_name || "",
      current_tenant_phone: rawDetail.current_tenant_phone || "",
      renewal_status: rawDetail.renewal_status,
      last_contact_result: rawDetail.last_contact_result || "",
      next_contact_date: rawDetail.next_contact_date || null,
      deposit_amount: toNullableNumber(rawDetail.deposit_amount),
      monthly_rent: toNullableNumber(rawDetail.monthly_rent),
      convertible_to_mortgage: rawDetail.convertible_to_mortgage,
      yearly_increase_percent: toNullableNumber(rawDetail.yearly_increase_percent),
    });
  }

  if (form.transaction_type === "MORTGAGE") {
    payload.detail = cleanObject({
      contract_start_date: rawDetail.contract_start_date || null,
      contract_end_date: rawDetail.contract_end_date || null,
      current_tenant_name: rawDetail.current_tenant_name || "",
      current_tenant_phone: rawDetail.current_tenant_phone || "",
      renewal_status: rawDetail.renewal_status,
      last_contact_result: rawDetail.last_contact_result || "",
      next_contact_date: rawDetail.next_contact_date || null,
      deposit_amount: toNullableNumber(rawDetail.deposit_amount),
    });
  }

  return payload;
}

function Field({ label, children }) {
  return (
    <label style={{ display: "grid", gap: 6 }}>
      <span style={{ fontSize: 14, fontWeight: 600 }}>{label}</span>
      {children}
    </label>
  );
}

function inputStyle() {
  return {
    width: "100%",
    padding: "10px 12px",
    border: "1px solid #d0d7de",
    borderRadius: 6,
    fontSize: 14,
    boxSizing: "border-box",
    background: "#fff",
  };
}

export default function PropertyFormPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState(baseInitialState);
  const [detailMap, setDetailMap] = useState(detailInitialState);
  const [submitting, setSubmitting] = useState(false);
  const [errorText, setErrorText] = useState("");
  const [successText, setSuccessText] = useState("");

  const currentDetail = useMemo(
    () => detailMap[form.transaction_type],
    [detailMap, form.transaction_type]
  );

  function updateForm(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }


  // مدیریت تغییرات چک‌باکس امکانات
  const handleAmenityChange = (amenity) => {
    setForm(prev => {
      const list = prev.amenities_list.includes(amenity)
        ? prev.amenities_list.filter(a => a !== amenity)
        : [...prev.amenities_list, amenity];
      return { ...prev, amenities_list: list };
    });
  };

  function updateDetail(key, value) {
    setDetailMap((prev) => ({
      ...prev,
      [form.transaction_type]: {
        ...prev[form.transaction_type],
        [key]: value,
      },
    }));
  }

async function handleSubmit(event) {
  event.preventDefault();

  setSubmitting(true);
  setErrorText("");
  setSuccessText("");

  try {
    const basePayload = buildPayload(form, detailMap);

    const finalAmenities = [
      ...(form.amenities_list || []),
      form.other_amenities,
    ].filter(Boolean).join("، ");


    const payload = {
      ...basePayload,
      amenities: finalAmenities,
      title:
        form.property_kind === "OTHER"
          ? `[${form.other_kind_name}] ${form.title}`
          : form.title,
      property_kind:
        form.property_kind === "OTHER"
          ? "OTHER"
          : form.property_kind,
    };

    await createProperty(payload);

    setSuccessText("ملک با موفقیت ثبت شد.");
    setForm(baseInitialState);
    setDetailMap(detailInitialState);

    setTimeout(() => navigate("/listings"), 900);
  } catch (error) {
    const apiError = error?.response?.data;

    setErrorText(
      typeof apiError === "string"
        ? apiError
        : JSON.stringify(apiError || { detail: "خطا در ثبت ملک" }, null, 2)
    );
  } finally {
    setSubmitting(false);
  }
}



  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: 24 }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 28 }}>ثبت ملک</h1>
        <p style={{ marginTop: 8, color: "#555" }}>
          این فرم مستقیماً به API ثبت ملک متصل است و فیلدهای جزئیات معامله را
          بر اساس نوع معامله تغییر می‌دهد.
        </p>
      </div>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 24 }}>
        <section style={{ display: "grid", gap: 16 }}>
          <h2 style={{ margin: 0, fontSize: 20 }}>اطلاعات اصلی</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 16 }}>
            <Field label="کد ملک">
              <input style={inputStyle()} value={form.code} onChange={(e) => updateForm("code", e.target.value)} />
            </Field>
            <Field label="عنوان">
              <input style={inputStyle()} value={form.title} onChange={(e) => updateForm("title", e.target.value)} />
            </Field>
            <Field label="نوع معامله">
              <select style={inputStyle()} value={form.transaction_type} onChange={(e) => updateForm("transaction_type", e.target.value)}>
                {transactionTypeOptions.map((item) => (
                  <option key={item.value} value={item.value}>{item.label}</option>
                ))}
              </select>
            </Field>

            <Field label="نوع ملک">
              <select style={inputStyle()} value={form.property_kind} onChange={(e) => updateForm("property_kind", e.target.value)}>
                {propertyKindOptions.map((item) => (
                  <option key={item.value} value={item.value}>{item.label}</option>
                ))}
              </select>
            </Field>
            <Field label="وضعیت">
              <select style={inputStyle()} value={form.status} onChange={(e) => updateForm("status", e.target.value)}>
                {statusOptions.map((item) => (
                  <option key={item.value} value={item.value}>{item.label}</option>
                ))}
              </select>
            </Field>
            <Field label="نوع سند">
              <select style={inputStyle()} value={form.document_type} onChange={(e) => updateForm("document_type", e.target.value)}>
                {documentTypeOptions.map((item) => (
                  <option key={item.value} value={item.value}>{item.label}</option>
                ))}
              </select>
            </Field>
          </div>
        </section>

        <section style={{ display: "grid", gap: 16 }}>
          <h2 style={{ margin: 0, fontSize: 20 }}>موقعیت</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 16 }}>
            <Field label="استان">
              <input style={inputStyle()} value={form.province} onChange={(e) => updateForm("province", e.target.value)} />
            </Field>
            <Field label="شهر">
              <input style={inputStyle()} value={form.city} onChange={(e) => updateForm("city", e.target.value)} />
            </Field>
            <Field label="منطقه">
              <input style={inputStyle()} value={form.district} onChange={(e) => updateForm("district", e.target.value)} />
            </Field>
          </div>

          <Field label="آدرس کامل">
            <textarea
              style={{ ...inputStyle(), minHeight: 90 }}
              value={form.full_address}
              onChange={(e) => updateForm("full_address", e.target.value)}
            />
          </Field>

          <Field label="لینک نقشه">
            <input style={inputStyle()} value={form.map_link} onChange={(e) => updateForm("map_link", e.target.value)} />
          </Field>
        </section>

        <section style={{ display: "grid", gap: 16 }}>
          <h2 style={{ margin: 0, fontSize: 20 }}>مشخصات فنی</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 16 }}>
            <Field label="متراژ بنا">
              <input style={inputStyle()} type="number" value={form.area_sqm} onChange={(e) => updateForm("area_sqm", e.target.value)} />
            </Field>
            <Field label="متراژ زمین">
              <input style={inputStyle()} type="number" value={form.land_area_sqm} onChange={(e) => updateForm("land_area_sqm", e.target.value)} />
            </Field>
            <Field label="تعداد خواب">
              <input style={inputStyle()} type="number" value={form.bedrooms} onChange={(e) => updateForm("bedrooms", e.target.value)} />
            </Field>
            <Field label="سال ساخت">
              <input style={inputStyle()} type="number" value={form.build_year} onChange={(e) => updateForm("build_year", e.target.value)} />
            </Field>

            <Field label="کل طبقات">
              <input style={inputStyle()} type="number" value={form.total_floors} onChange={(e) => updateForm("total_floors", e.target.value)} />
            </Field>
            <Field label="طبقه واحد">
              <input style={inputStyle()} type="number" value={form.unit_floor} onChange={(e) => updateForm("unit_floor", e.target.value)} />
            </Field>
            <Field label="واحد در هر طبقه">
              <input style={inputStyle()} type="number" value={form.units_per_floor} onChange={(e) => updateForm("units_per_floor", e.target.value)} />
            </Field>
            <Field label="جهت">
              <input style={inputStyle()} value={form.direction} onChange={(e) => updateForm("direction", e.target.value)} />
            </Field>

            <Field label="تعداد پارکینگ">
              <input style={inputStyle()} type="number" value={form.parking_count} onChange={(e) => updateForm("parking_count", e.target.value)} />
            </Field>
            <Field label="سیستم گرمایش">
              <input style={inputStyle()} value={form.heating_system} onChange={(e) => updateForm("heating_system", e.target.value)} />
            </Field>
            <Field label="سیستم سرمایش">
              <input style={inputStyle()} value={form.cooling_system} onChange={(e) => updateForm("cooling_system", e.target.value)} />
            </Field>
            <Field label="کف پوش">
              <input style={inputStyle()} value={form.floor_covering} onChange={(e) => updateForm("floor_covering", e.target.value)} />
            </Field>
          </div>

          <Field label="امکانات رفاهی">
            <input
              style={inputStyle()}
              value={form.amenities}
              onChange={(e) => updateForm("amenities", e.target.value)}
              placeholder="مثال: آسانسور، پارکینگ، انباری"
            />
          </Field>

          <Field label="وضعیت واحد">
            <input style={inputStyle()} value={form.unit_condition} onChange={(e) => updateForm("unit_condition", e.target.value)} />
          </Field>

          <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
            <label><input type="checkbox" checked={form.has_elevator} onChange={(e) => updateForm("has_elevator", e.target.checked)} /> آسانسور</label>
            <label><input type="checkbox" checked={form.has_storage} onChange={(e) => updateForm("has_storage", e.target.checked)} /> انباری</label>
            <label><input type="checkbox" checked={form.has_balcony} onChange={(e) => updateForm("has_balcony", e.target.checked)} /> بالکن</label>
            <label><input type="checkbox" checked={form.is_renovated} onChange={(e) => updateForm("is_renovated", e.target.checked)} /> بازسازی شده</label>
          </div>
        </section>

        <section style={{ display: "grid", gap: 16 }}>
          <h2 style={{ margin: 0, fontSize: 20 }}>اطلاعات مالک</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 16 }}>
            <Field label="نام مالک">
              <input style={inputStyle()} value={form.owner_name} onChange={(e) => updateForm("owner_name", e.target.value)} />
            </Field>
            <Field label="شماره مالک">
              <input style={inputStyle()} value={form.owner_phone} onChange={(e) => updateForm("owner_phone", e.target.value)} />
            </Field>
            <label style={{ alignSelf: "end" }}>
              <input type="checkbox" checked={form.is_exclusive} onChange={(e) => updateForm("is_exclusive", e.target.checked)} /> فایل انحصاری
            </label>
          </div>
        </section>

        <section style={{ display: "grid", gap: 16 }}>
          <h2 style={{ margin: 0, fontSize: 20 }}>توضیحات</h2>
          <Field label="توضیحات عمومی">
            <textarea style={{ ...inputStyle(), minHeight: 100 }} value={form.public_description} onChange={(e) => updateForm("public_description", e.target.value)} />
          </Field>
          <Field label="یادداشت خصوصی">
            <textarea style={{ ...inputStyle(), minHeight: 100 }} value={form.private_note} onChange={(e) => updateForm("private_note", e.target.value)} />
          </Field>
        </section>

        <section style={{ display: "grid", gap: 16 }}>
          <h2 style={{ margin: 0, fontSize: 20 }}>جزئیات معامله</h2>

          {form.transaction_type === "SALE" && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 16 }}>
              <Field label="قیمت کل">
                <input style={inputStyle()} type="number" value={currentDetail.total_price} onChange={(e) => updateDetail("total_price", e.target.value)} />
              </Field>
              <Field label="قیمت هر متر">
                <input style={inputStyle()} type="number" value={currentDetail.price_per_sqm} onChange={(e) => updateDetail("price_per_sqm", e.target.value)} />
              </Field>
              <Field label="نوع پرداخت">
                <select style={inputStyle()} value={currentDetail.payment_terms} onChange={(e) => updateDetail("payment_terms", e.target.value)}>
                  {paymentTermsOptions.map((item) => (
                    <option key={item.value} value={item.value}>{item.label}</option>
                  ))}
                </select>
              </Field>
              <Field label="پیش پرداخت">
                <input style={inputStyle()} type="number" value={currentDetail.down_payment} onChange={(e) => updateDetail("down_payment", e.target.value)} />
              </Field>
              <label style={{ alignSelf: "end" }}>
                <input type="checkbox" checked={currentDetail.is_exchangeable} onChange={(e) => updateDetail("is_exchangeable", e.target.checked)} /> قابل معاوضه
              </label>
            </div>
          )}

          {form.transaction_type === "PRESALE" && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 16 }}>
              <Field label="قیمت کل قرارداد">
                <input style={inputStyle()} type="number" value={currentDetail.total_contract_price} onChange={(e) => updateDetail("total_contract_price", e.target.value)} />
              </Field>
              <Field label="سازنده">
                <input style={inputStyle()} value={currentDetail.builder_company} onChange={(e) => updateDetail("builder_company", e.target.value)} />
              </Field>
              <Field label="درصد پیشرفت">
                <input style={inputStyle()} type="number" value={currentDetail.progress_percent} onChange={(e) => updateDetail("progress_percent", e.target.value)} />
              </Field>
              <Field label="تاریخ تحویل">
                <input style={inputStyle()} type="date" value={currentDetail.estimated_delivery_date} onChange={(e) => updateDetail("estimated_delivery_date", e.target.value)} />
              </Field>
              <Field label="مبلغ پرداخت شده">
                <input style={inputStyle()} type="number" value={currentDetail.amount_paid} onChange={(e) => updateDetail("amount_paid", e.target.value)} />
              </Field>
              <Field label="مانده پرداخت">
                <input style={inputStyle()} type="number" value={currentDetail.amount_remaining} onChange={(e) => updateDetail("amount_remaining", e.target.value)} />
              </Field>
              <Field label="شرایط اقساط">
                <input style={inputStyle()} value={currentDetail.installment_terms} onChange={(e) => updateDetail("installment_terms", e.target.value)} />
              </Field>
              <Field label="شماره قرارداد">
                <input style={inputStyle()} value={currentDetail.contract_number} onChange={(e) => updateDetail("contract_number", e.target.value)} />
              </Field>
            </div>
          )}

          {(form.transaction_type === "RENT" || form.transaction_type === "MORTGAGE") && (
            <div style={{ display: "grid", gap: 16 }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 16 }}>
                <Field label="شروع قرارداد">
                  <input style={inputStyle()} type="date" value={currentDetail.contract_start_date} onChange={(e) => updateDetail("contract_start_date", e.target.value)} />
                </Field>
                <Field label="پایان قرارداد">
                  <input style={inputStyle()} type="date" value={currentDetail.contract_end_date} onChange={(e) => updateDetail("contract_end_date", e.target.value)} />
                </Field>
                <Field label="وضعیت تمدید">
                  <select style={inputStyle()} value={currentDetail.renewal_status} onChange={(e) => updateDetail("renewal_status", e.target.value)}>
                    {renewalStatusOptions.map((item) => (
                      <option key={item.value} value={item.value}>{item.label}</option>
                    ))}
                  </select>
                </Field>

                <Field label="نام مستاجر">
                    <input
                        style={inputStyle()}
                        value={currentDetail.current_tenant_name}
                        onChange={(e) =>
                        updateDetail("current_tenant_name", e.target.value)
                        }
                    />
                    </Field>

                    <Field label="شماره مستاجر">
                    <input
                        style={inputStyle()}
                        value={currentDetail.current_tenant_phone}
                        onChange={(e) =>
                        updateDetail("current_tenant_phone", e.target.value)
                        }
                    />
                    </Field>

                    <Field label="نتیجه آخرین تماس">
                    <input
                        style={inputStyle()}
                        value={currentDetail.last_contact_result}
                        onChange={(e) =>
                        updateDetail("last_contact_result", e.target.value)
                        }
                    />
                    </Field>

                    <Field label="تاریخ تماس بعدی">
                    <input
                        style={inputStyle()}
                        type="date"
                        value={currentDetail.next_contact_date}
                        onChange={(e) =>
                        updateDetail("next_contact_date", e.target.value)
                        }
                    />
                    </Field>

                    <Field label="مبلغ رهن">
                    <input
                        style={inputStyle()}
                        type="number"
                        min="0"
                        value={currentDetail.deposit_amount}
                        onChange={(e) =>
                        updateDetail("deposit_amount", e.target.value)
                        }
                    />
                    </Field>


                {form.transaction_type === "RENT" && (
                  <>
                    <Field label="اجاره ماهانه">
                      <input
                        style={inputStyle()}
                        type="number"
                        min="0"
                        value={currentDetail.monthly_rent}
                        onChange={(e) =>
                          updateDetail("monthly_rent", e.target.value)
                        }
                      />
                    </Field>

                    <Field label="درصد افزایش سالانه">
                      <input
                        style={inputStyle()}
                        type="number"
                        min="0"
                        step="0.01"
                        value={currentDetail.yearly_increase_percent}
                        onChange={(e) =>
                          updateDetail(
                            "yearly_increase_percent",
                            e.target.value
                          )
                        }
                      />
                    </Field>

                    <label style={{ alignSelf: "end" }}>
                      <input
                        type="checkbox"
                        checked={currentDetail.convertible_to_mortgage}
                        onChange={(e) =>
                          updateDetail(
                            "convertible_to_mortgage",
                            e.target.checked
                          )
                        }
                      />{" "}
                      قابلیت تبدیل به رهن دارد
                    </label>
                  </>
                )}
              </div>
            </div>
          )}
        </section>

        {errorText && (
          <pre
            style={{
              margin: 0,
              padding: 16,
              whiteSpace: "pre-wrap",
              overflowX: "auto",
              color: "#991b1b",
              background: "#fee2e2",
              border: "1px solid #fecaca",
              borderRadius: 8,
              direction: "ltr",
              textAlign: "left",
            }}
          >
            {errorText}
          </pre>
        )}

        {successText && (
          <div
            style={{
              padding: 16,
              color: "#166534",
              background: "#dcfce7",
              border: "1px solid #bbf7d0",
              borderRadius: 8,
            }}
          >
            {successText}
          </div>
        )}

        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            gap: 12,
            paddingBottom: 32,
          }}
        >
          <button
            type="button"
            onClick={() => navigate("/listings")}
            disabled={submitting}
            style={{
              padding: "10px 18px",
              border: "1px solid #d0d7de",
              borderRadius: 6,
              cursor: submitting ? "not-allowed" : "pointer",
              background: "#fff",
            }}
          >
            انصراف
          </button>

          <button
            type="submit"
            disabled={submitting}
            style={{
              padding: "10px 18px",
              border: "none",
              borderRadius: 6,
              cursor: submitting ? "not-allowed" : "pointer",
              color: "#fff",
              background: submitting ? "#94a3b8" : "#2563eb",
            }}
          >
            {submitting ? "در حال ثبت ملک…" : "ثبت ملک"}
          </button>
        </div>
      </form>
    </div>
  );
}
