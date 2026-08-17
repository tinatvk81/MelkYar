import client from "./client";

export async function getListings(params = {}) {
  const response = await client.get("/properties/listings/", {
    params,
  });

  return response.data;
}
export async function getPropertyDetail(id) {
  const response = await client.get(`/properties/listings/${id}/`);
  return response.data;
}
