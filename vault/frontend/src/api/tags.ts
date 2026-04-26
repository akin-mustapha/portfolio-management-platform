import client from "./client";

export async function fetchTags() {
  const { data } = await client.get("/tags");
  return data;
}

export async function assignTag(ticker: string, tagId: number) {
  const { data } = await client.put(`/assets/${ticker}/tags`, {
    tag_id: tagId,
  });
  return data;
}
