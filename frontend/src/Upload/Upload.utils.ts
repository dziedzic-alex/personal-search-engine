export const ALLOWED_FILE_TYPES = [
  "application/pdf",
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/heic",
  "image/heif",
];

export const ALLOWED_FILE_EXTENSIONS = [
  "pdf",
  "jpeg",
  "jpg",
  "png",
  "webp",
  "heic",
  "heif",
];

export function isFileAllowed(file: File): boolean {
  return (
    ALLOWED_FILE_TYPES.includes(file.type) ||
    ALLOWED_FILE_EXTENSIONS.includes(
      file.name.split(".").pop()?.toLowerCase() ?? "",
    )
  );
}
