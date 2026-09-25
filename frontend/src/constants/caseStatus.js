export const CASE_STATUSES = [
  { value: 'open', label: 'Open' },
  { value: 'in_progress', label: 'In progress' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'written_off', label: 'Written off' },
];

export const CASE_STATUS_LABELS = Object.fromEntries(CASE_STATUSES.map((s) => [s.value, s.label]));
