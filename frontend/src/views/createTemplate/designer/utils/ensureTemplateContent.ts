import { cloneDeep } from 'lodash';

import { getUuid } from '@/utils/common';
import { HJNewSchema } from '../schema/template';
import pageSchemas from '../schema/pageSchema';
import modulesList from '../schema';
import { useSetModuleSchema } from '../hooks/useSetModuleSchema';

interface EnsureOptions {
  templateId?: string;
  title?: string;
  pageName?: string;
}

const DEFAULT_TITLE = '猫步简历';
const DEFAULT_PAGE = 'BasePage';
const DEFAULT_MODULE_ORDER = [
  'resume_title',
  'base_info',
  'job_intention',
  'edu_background',
  'skill_specialties',
  'campus_experience',
  'internship_experience',
  'work_experience',
  'project_experience',
  'awards',
  'hobbies',
  'self_evaluation'
];

const hashString = (value: string) => {
  let hash = 0;
  for (let i = 0; i < value.length; i++) {
    hash = (hash << 5) - hash + value.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
};

const resolvePageName = (pageName?: string) => {
  if (pageName && (pageSchemas as any)[pageName]) {
    return pageName;
  }
  return DEFAULT_PAGE;
};

const createBaseTemplate = (title?: string, pageName?: string) => {
  const resolvedPageName = resolvePageName(pageName);
  const pageSchema = cloneDeep((pageSchemas as any)[resolvedPageName] || HJNewSchema);
  pageSchema.id = getUuid();
  pageSchema.componentsTree = [];
  pageSchema.props = pageSchema.props || {};
  pageSchema.props.pageName = resolvedPageName;
  pageSchema.props.title = title || pageSchema.props.title || DEFAULT_TITLE;
  pageSchema.config = pageSchema.config || {};
  pageSchema.config.title = title || pageSchema.config.title || DEFAULT_TITLE;
  pageSchema.config.layout = pageSchema.config.layout || { children: [] };
  return pageSchema;
};

const createStarterModules = (seedText: string) => {
  const modules: any[] = [];
  const baseSeed = hashString(seedText || 'starter-template');
  DEFAULT_MODULE_ORDER.forEach((categoryKey, index) => {
    const category = (modulesList as any)?.[categoryKey];
    const list = category?.list;
    if (!Array.isArray(list) || !list.length) {
      return;
    }
    const variantIndex = (baseSeed + index * 7) % list.length;
    const raw = cloneDeep(list[variantIndex]);
    if (!raw) {
      return;
    }
    modules.push(useSetModuleSchema(raw));
  });
  return modules;
};

export const buildStarterTemplateContent = (options: EnsureOptions = {}) => {
  const base = createBaseTemplate(options.title, options.pageName);
  const seedText = options.templateId || options.title || DEFAULT_TITLE;
  base.componentsTree = createStarterModules(seedText);
  return base;
};

export const ensureTemplateContent = (templateJson: any, options: EnsureOptions = {}) => {
  const title = options.title || DEFAULT_TITLE;
  const pageName = options.pageName || templateJson?.props?.pageName;

  if (templateJson && typeof templateJson === 'object') {
    const normalized = cloneDeep(templateJson);
    normalized.id = normalized.id || getUuid();
    normalized.props = normalized.props || {};
    normalized.props.pageName = resolvePageName(pageName);
    normalized.props.title = normalized.props.title || title;
    normalized.config = normalized.config || {};
    normalized.config.title = normalized.config.title || title;
    normalized.config.layout = normalized.config.layout || { children: [] };
    normalized.componentsTree = Array.isArray(normalized.componentsTree)
      ? normalized.componentsTree
      : [];

    if (normalized.componentsTree.length > 0) {
      return normalized;
    }
  }

  return buildStarterTemplateContent({
    templateId: options.templateId,
    title,
    pageName
  });
};
