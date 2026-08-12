import { useEffect, useState } from "react";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function ListingsPage() {
  const [data, setData] = useState({ results: [] });
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const { logout } = useAuth();

  const fetchListings = async (params = {}) => {
    setLoading(true);
    try {
      const response = await client.get("/api/properties/listings/", { params });
      setData(response.data);
    } catch (error) {
      setData({ results: [] });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchListings();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchListings(search ? { search } : {});
  };

  return (
    <div className="container">
      <header className="topbar">
        <div>
          <h1>فایل‌های ملکی</h1>
          <p>ورود با حساب مدیر انجام شده است.</p>
        </div>
        <button type="button" onClick={logout}>
          خروج
        </button>
      </header>

      <form className="searchbar" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="جستجو بر اساس کد، عنوان، شهر..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button type="submit">جستجو</button>
      </form>

      {loading ? (
        <p>در حال بارگذاری...</p>
      ) : data.results.length === 0 ? (
        <p>موردی یافت نشد.</p>
      ) : (
        <div className="grid">
          {data.results.map((item) => (
            <article className="card" key={item.id}>
              <h2>{item.title || "بدون عنوان"}</h2>
              <p><strong>کد:</strong> {item.code || "-"}</p>
              <p><strong>شهر:</strong> {item.city || "-"}</p>
              <p><strong>منطقه:</strong> {item.district || "-"}</p>
              <p><strong>نوع معامله:</strong> {item.transaction_type || "-"}</p>
              <p><strong>وضعیت:</strong> {item.status || "-"}</p>
              <p><strong>متراژ:</strong> {item.area_sqm || "-"}</p>
              <p>
                <strong>امکانات:</strong>{" "}
                {item.property_amenities?.length
                  ? item.property_amenities.map((x) => x.name).join("، ")
                  : "-"}
              </p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
