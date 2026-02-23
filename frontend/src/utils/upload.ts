export const resolveUploadFileUrl = (response: any): string => {
  const candidates = [
    response?.data?.fileUrl,
    response?.data?.url,
    response?.data?.data?.fileUrl,
    response?.data?.data?.url,
    response?.fileUrl,
    response?.url
  ];

  const match = candidates.find((item) => typeof item === 'string' && item.trim().length > 0);
  return match ? match.trim() : '';
};
