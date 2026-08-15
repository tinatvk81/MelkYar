import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { logout } from "../api/auth";
import { getListings } from "../api/properties";

const transactionTypeLabels = {
  SALE: "فروش",
  PRESALE: "پیش‌فروش",
  RENT: "اجاره",
  MORTGAGE: "رهن کامل",
};

const statusLabels = {
  ACTIVE: "فعال",
  RESERVED: "رزرو",
  CLOSED: "بسته‌شده",
  INACTIVE: "غیرفعال",
};

function formatNumber(value) {
  if (!value) return "—";
  return new Intl.NumberFormat("fa-IR").format(value);
}

function getImageUrl(path) {
  if (!path) return "";
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  // فرض بر این است که VITE_API_BASE_URL انتهای آن اسلش ندارد
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";
  return `${baseUrl}${path}`;
}

export default function ListingsPage() {
  const navigate = useNavigate();

  const [selectedProperty, setSelectedProperty] = useState(null);
  const [data, setData] = useState({ count: 0, next: null, previous: null, results: [] });
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState({
    transaction_type: "",
    city: "",
    area_min: "",
  });

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const response = await getListings({
          page,
          search: search || undefined,
          ...filters,
          ordering: "-updated_at",
        });
        setData(response);
      } catch (err) {
        setErrorMessage("خطا در بارگذاری داده‌ها");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [page, search, filters]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
    setPage(1);
  };

  return (
    <main className="dashboard-page">
      <header className="topbar">
        <div>
          <h1>فایل‌های ملکی</h1>
          <p>مدیریت و فیلتر پیشرفته فایل‌ها</p>
        </div>
        <button className="secondary-button" onClick={() => { logout(); navigate("/login"); }}>خروج</button>
      </header>

      <div className="layout-with-sidebar">
        <aside className="filter-sidebar">
          <h3>فیلترها</h3>
          <div className="filter-group">
            <label>نوع معامله</label>
            <select name="transaction_type" value={filters.transaction_type} onChange={handleFilterChange}>
              <option value="">همه</option>
              <option value="SALE">فروش</option>
              <option value="RENT">اجاره</option>
              <option value="MORTGAGE">رهن کامل</option>
            </select>
          </div>
          <div className="filter-group">
            <label>شهر</label>
            <input name="city" placeholder="مثلاً: مشهد" value={filters.city} onChange={handleFilterChange} />
          </div>
          <div className="filter-group">
            <label>حداقل متراژ</label>
            <input type="number" name="area_min" value={filters.area_min} onChange={handleFilterChange} />
          </div>
          <button className="text-button" onClick={() => setFilters({transaction_type: "", city: "", area_min: ""})}>
            پاکسازی فیلترها
          </button>
        </aside>

        <section className="main-content">
          <div className="listing-toolbar">
            <input 
              className="search-input"
              placeholder="جست‌وجو در عنوان، آدرس یا کد..." 
              value={search} 
              onChange={(e) => setSearch(e.target.value)} 
            />
          </div>

          {isLoading ? (
            <div className="loading-state">در حال بارگذاری...</div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>کد</th>
                    <th>عنوان</th>
                    <th>نوع</th>
                    <th>مکان</th>
                    <th>متراژ</th>
                    <th>وضعیت</th>
                  </tr>
                </thead>
                <tbody>
                  {data.results.map(item => (
                    <tr key={item.id} onClick={() => setSelectedProperty(item)}>
                      <td className="code-cell">{item.code}</td>
                      <td>{item.title}</td>
                      <td>{transactionTypeLabels[item.transaction_type]}</td>
                      <td>{item.city} / {item.district}</td>
                      <td>{formatNumber(item.area_sqm)} متر</td>
                      <td><span className={`status status-${item.status}`}>{statusLabels[item.status]}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <footer className="pagination">
            <div style={{marginTop: '20px', display: 'flex', gap: '10px', alignItems: 'center'}}>
               <button className="secondary-button" disabled={!data.previous} onClick={() => setPage(p => p - 1)}>قبلی</button>
               <span>صفحه {page}</span>
               <button className="secondary-button" disabled={!data.next} onClick={() => setPage(p => p + 1)}>بعدی</button>
            </div>
          </footer>
        </section>
      </div>

      {selectedProperty && (
        <div className="modal-overlay" onClick={() => setSelectedProperty(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <header className="modal-header">
              <h2>جزئیات ملک: {selectedProperty.code}</h2>
              <button style={{fontSize: '24px', background: 'none', border: 'none'}} onClick={() => setSelectedProperty(null)}>×</button>
            </header>
            <div className="modal-body">
              <div className="detail-grid">
                <div><strong>عنوان:</strong> {selectedProperty.title}</div>
                <div><strong>نوع معامله:</strong> {transactionTypeLabels[selectedProperty.transaction_type]}</div>
                <div><strong>متراژ:</strong> {formatNumber(selectedProperty.area_sqm)} متر</div>
                <div><strong>اتاق:</strong> {selectedProperty.bedrooms || 0}</div>
              </div>
              <div className="special-details">
                <h3>اطلاعات مالی</h3>
                {selectedProperty.transaction_type === 'SALE' ? (
                  <p>قیمت کل: <strong>{formatNumber(selectedProperty.detail_data?.total_price)} تومان</strong></p>
                ) : (
                  <>
                    <p>ودیعه: <strong>{formatNumber(selectedProperty.detail_data?.deposit_amount)} تومان</strong></p>
                    <p>اجاره: <strong>{formatNumber(selectedProperty.detail_data?.monthly_rent_amount)} تومان</strong></p>
                  </>
                )}
              </div>
              <div>
                <h3>توضیحات</h3>
                <p>{selectedProperty.public_description || 'ندارد'}</p>
              </div>
              {selectedProperty.property_amenities?.length > 0 && (
                <div style={{marginTop: '20px'}}>
                  <h3>امکانات</h3>
                  {selectedProperty.property_amenities.map(a => (
                    <span key={a.id} className="amenity-badge">{a.name}</span>
                  ))}
                </div>
              )}
              <div className="images-section">
                <h3>تصاویر ملک</h3>
                {selectedProperty.images && selectedProperty.images.length > 0 ? (
                  <div className="images-grid">
                    {selectedProperty.images.map((img) => (
                      <figure key={img.id} className="property-image-card">
                        <img
                          src={getImageUrl(img.image)}
                          alt={img.caption || "تصویر ملک"}
                          className="property-image"
                        />
                        {img.caption && <figcaption>{img.caption}</figcaption>}
                      </figure>
                    ))}
                  </div>
                ) : (
                  <p className="no-data">تصویری ثبت نشده است.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
