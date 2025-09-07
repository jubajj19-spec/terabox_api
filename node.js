export default {
  async fetch(request) {
    const { searchParams } = new URL(request.url);
    const link = searchParams.get("url");
    if (!link) {
      return Response.json({ success: false, error: "Missing url" }, { status: 400 });
    }

    // Call backend API
    const backendResponse = await fetch(`https://YOUR_BACKEND_DOMAIN/v1/terabox?url=${encodeURIComponent(link)}`);
    const data = await backendResponse.json();

    return Response.json(data);
  }
};