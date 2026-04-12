/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docsSidebar: [
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: ['intro', 'installation', 'quickstart'],
    },
    {
      type: 'category',
      label: 'DSL Reference',
      collapsed: false,
      items: [
        'dsl/overview',
        'dsl/primitives',
        'dsl/operations',
        'dsl/transforms',
        'dsl/curves',
        'dsl/instancing',
        'dsl/field-nodes',
        'dsl/math-ops',
      ],
    },
    {
      type: 'category',
      label: 'Backends',
      collapsed: false,
      items: [
        'backends/overview',
        'backends/blender',
        'backends/opencascade',
        'backends/openscad',
        'backends/jscad',
      ],
    },
    {
      type: 'category',
      label: 'IR Layer',
      items: ['ir/overview'],
    },
    {
      type: 'category',
      label: 'Mori Ecosystem',
      items: [
        'mori/overview',
        'mori/halo-maps',
        'mori/print-labo',
      ],
    },
  ],
};

module.exports = sidebars;
