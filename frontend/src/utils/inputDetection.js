// frontend/src/utils/inputDetection.js

export const INPUT_TYPES = {
  ARXIV_ID: 'arxiv_id',
  ARXIV_URL: 'arxiv_url',
  PLATFORM_URL: 'platform_url',
  TOPIC: 'topic',
};

const PATTERNS = {
  arxiv_id_new: /^\d{4}\.\d{4,5}$/,
  arxiv_id_old: /^[a-z-]+\/\d+$/,
  arxiv_url: /arxiv\.org/,
  platform_urls: ['alphaxiv.org', 'huggingface.co', 'paperswithcode.com', 'semanticscholar.org'],
};

export function detectInputType(input) {
  const trimmed = input.trim().toLowerCase();

  if (PATTERNS.arxiv_url.test(trimmed)) {
    return INPUT_TYPES.ARXIV_URL;
  }

  if (PATTERNS.platform_urls.some(domain => trimmed.includes(domain))) {
    return INPUT_TYPES.PLATFORM_URL;
  }

  if (PATTERNS.arxiv_id_new.test(trimmed) || PATTERNS.arxiv_id_old.test(trimmed)) {
    return INPUT_TYPES.ARXIV_ID;
  }

  return INPUT_TYPES.TOPIC;
}

export function getInputTypeLabel(type) {
  const labels = {
    [INPUT_TYPES.ARXIV_ID]: 'arXiv ID',
    [INPUT_TYPES.ARXIV_URL]: 'arXiv URL',
    [INPUT_TYPES.PLATFORM_URL]: 'Platform URL',
    [INPUT_TYPES.TOPIC]: 'Topic Search',
  };
  return labels[type] || 'Unknown';
}
