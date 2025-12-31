import js from '@eslint/js';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';
import simpleImportSort from 'eslint-plugin-simple-import-sort';
import unusedImports from 'eslint-plugin-unused-imports';

/** Shared plugins */
const sharedPlugins = {
  'unused-imports': unusedImports,
  'simple-import-sort': simpleImportSort,
};

/** Shared rules (JS + TS) */
const sharedRules = {
  'no-unused-vars': 'off',
  'no-undef': 'off',

  'simple-import-sort/imports': 'error',
  'simple-import-sort/exports': 'error',

  'unused-imports/no-unused-imports': 'error',
  'unused-imports/no-unused-vars': [
    'warn',
    {
      vars: 'all',
      varsIgnorePattern: '^_',
      args: 'after-used',
      argsIgnorePattern: '^_',
    },
  ],
};

export default [
  js.configs.recommended,
  // JS files
  {
    files: ['**/*.{js,jsx}'],
    plugins: sharedPlugins,
    rules: sharedRules,
  },
  // TS files
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        project: './tsconfig.json',
      },
    },
    plugins: {
      ...sharedPlugins,
      // TS-only plugins
      '@typescript-eslint': tseslint,
    },
    rules: {
      ...sharedRules,
      // TS-only rules
      'no-redeclare': 'off',
      '@typescript-eslint/no-unnecessary-condition': 'error',
    },
  },
];
