import { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Autocomplete,
  TextField,
  CircularProgress,
  Alert,
} from "@mui/material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchTags, assignTag } from "../../api/tags";

interface EditTagsModalProps {
  open: boolean;
  onClose: () => void;
  ticker: string;
  currentTags: string[];
}

export default function EditTagsModal({
  open,
  onClose,
  ticker,
  currentTags,
}: EditTagsModalProps) {
  const qc = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const { data: allTags = [] } = useQuery({
    queryKey: ["tags"],
    queryFn: fetchTags,
    enabled: open,
  });

  const tagOptions = allTags as Array<{ id: number; name: string }>;

  const mutation = useMutation({
    mutationFn: ({ tagId }: { tagId: number }) => assignTag(ticker, tagId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["portfolio", "summary"] });
      qc.invalidateQueries({ queryKey: ["assets"] });
      setError(null);
    },
    onError: (e: Error) => setError(e.message),
  });

  const handleAssign = (option: { id: number; name: string } | null) => {
    if (option) mutation.mutate({ tagId: option.id });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ fontSize: 14, fontWeight: 700 }}>
        Assign Tags — {ticker}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 1, fontSize: 12 }}>
            {error}
          </Alert>
        )}
        <TextField
          label="Current Tags"
          value={currentTags.join(", ") || "None"}
          InputProps={{ readOnly: true }}
          size="small"
          fullWidth
          sx={{ mb: 2 }}
        />
        <Autocomplete
          options={tagOptions}
          getOptionLabel={(o) => o.name}
          onChange={(_, val) => handleAssign(val)}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Add Tag"
              size="small"
              InputProps={{
                ...params.InputProps,
                endAdornment: (
                  <>
                    {mutation.isPending ? <CircularProgress size={14} /> : null}
                    {params.InputProps.endAdornment}
                  </>
                ),
              }}
            />
          )}
        />
      </DialogContent>
      <DialogActions>
        <Button size="small" onClick={onClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
}
