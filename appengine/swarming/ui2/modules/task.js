export const ONGOING_STATES = [
  'PENDING',
  'RUNNING'
];

export const COMPL_STATES = [
  'COMPLETED_SUCCESS',
  'COMPLETED_FAILURE',
];

export const NON_COMPL_EXCEP_STATES = [
  'TIMED_OUT',
  'EXPIRED',
  'NO_RESOURCE',
  'CANCELED',
  'KILLED',
];

export const NON_COMPL_STATES = [
  'BOT_DIED',
  'DEDUPED'
].push(...NON_COMPL_EXCEP_STATES);

export const COUNT_STATES = []
  .push(...COMPL_STATES)
  .push(...ONGOING_STATES)
  .push(...NON_COMPL_STATES)

export const FILTER_STATES = [
  'ALL',
  'COMPLETED',
  'PENDING_RUNNING',
].push(...COUNT_STATES);
