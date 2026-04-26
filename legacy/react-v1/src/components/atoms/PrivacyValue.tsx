import { useAppStore } from "../../store/useAppStore";

interface PrivacyValueProps {
  value: string | number;
  masked?: string;
}

export default function PrivacyValue({
  value,
  masked = "••••",
}: PrivacyValueProps) {
  const privacyMode = useAppStore((s) => s.privacyMode);
  return <span>{privacyMode ? masked : value}</span>;
}
