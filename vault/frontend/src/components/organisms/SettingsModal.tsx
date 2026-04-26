import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  InputAdornment,
  TextField,
} from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import { useQuery, useMutation } from "@tanstack/react-query";
import { fetchCredentials, saveCredentials } from "../../api/credentials";

interface SettingsModalProps {
  open: boolean;
  onClose: () => void;
}

export default function SettingsModal({ open, onClose }: SettingsModalProps) {
  const [apiKey, setApiKey] = useState("");
  const [secretToken, setSecretToken] = useState("");
  const [apiUrl, setApiUrl] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data } = useQuery({
    queryKey: ["credentials"],
    queryFn: fetchCredentials,
    enabled: open,
  });

  useEffect(() => {
    if (data) {
      setApiKey((data as Record<string, string>).api_key ?? "");
      setSecretToken((data as Record<string, string>).secret_token ?? "");
      setApiUrl((data as Record<string, string>).api_url ?? "");
    }
  }, [data]);

  const save = useMutation({
    mutationFn: () =>
      saveCredentials({
        api_key: apiKey,
        secret_token: secretToken,
        api_url: apiUrl,
      }),
    onSuccess: () => {
      setSuccess(true);
      setError(null);
    },
    onError: (e: Error) => {
      setError(e.message);
      setSuccess(false);
    },
  });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ fontSize: 14, fontWeight: 700 }}>
        API Credentials
      </DialogTitle>
      <DialogContent
        sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 2 }}
      >
        {success && (
          <Alert severity="success" sx={{ fontSize: 12 }}>
            Credentials saved.
          </Alert>
        )}
        {error && (
          <Alert severity="error" sx={{ fontSize: 12 }}>
            {error}
          </Alert>
        )}

        <TextField
          label="API Key"
          size="small"
          fullWidth
          type={showKey ? "text" : "password"}
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton size="small" onClick={() => setShowKey((v) => !v)}>
                  {showKey ? (
                    <VisibilityOffIcon fontSize="small" />
                  ) : (
                    <VisibilityIcon fontSize="small" />
                  )}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <TextField
          label="Secret Token"
          size="small"
          fullWidth
          type="password"
          value={secretToken}
          onChange={(e) => setSecretToken(e.target.value)}
        />

        <TextField
          label="API URL"
          size="small"
          fullWidth
          value={apiUrl}
          onChange={(e) => setApiUrl(e.target.value)}
        />
      </DialogContent>
      <DialogActions>
        <Button size="small" onClick={onClose}>
          Cancel
        </Button>
        <Button
          size="small"
          variant="contained"
          onClick={() => save.mutate()}
          disabled={save.isPending || !apiKey}
        >
          {save.isPending ? <CircularProgress size={14} /> : "Save"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
