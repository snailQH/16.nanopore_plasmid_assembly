# Project Rules Documentation

This directory contains all project rules and guidelines for the n8n Manager project.

## Rules Overview

### Core Rules

1. **rules.mdc** - Main project rules and critical guidelines
   - Project context and technologies
   - Mandatory first steps
   - Code reuse requirements
   - Documentation requirements
   - n8n-specific rules

2. **general.mdc** - General development practices
   - Project context understanding (MANDATORY)
   - Code quality standards
   - Documentation requirements
   - Error handling

3. **n8n_development.mdc** - n8n workflow development rules
   - Workflow design principles
   - Template organization
   - Documentation requirements
   - Testing and validation
   - Credential management

4. **memory_management.mdc** - Agent memory management rules
   - Cursor memory features usage
   - Documentation as memory
   - Memory maintenance workflow
   - Memory quality standards

### Supporting Rules

4. **code_reuse.mdc** - Code reuse and consolidation
   - Analyze existing code first
   - Extend before creating
   - Consolidate duplicates

5. **project_organization.mdc** - File organization
   - Directory structure
   - Naming conventions
   - Documentation organization

## Rule Hierarchy

```
rules.mdc (Main Rules)
├── general.mdc (General Practices)
│   └── Project Context Understanding (MANDATORY FIRST STEP)
├── n8n_development.mdc (n8n-Specific)
├── memory_management.mdc (Memory Management)
├── code_reuse.mdc (Code Reuse)
└── project_organization.mdc (File Organization)
```

## Key Principles

### 1. Documentation First
- **MANDATORY**: Read all relevant documentation before starting any task
- **MANDATORY**: Update CHANGE_LOGS.md after completing tasks
- **MANDATORY**: Keep README.md current
- All documentation must be in English

### 2. Code Reuse
- Analyze existing code before creating new
- Extend existing templates/workflows when possible
- Consolidate duplicate code
- Reference existing implementations

### 3. n8n Best Practices
- Follow n8n workflow design principles
- Use proper credential management
- Test workflows thoroughly
- Document all configurations

### 4. Project Organization
- Follow established directory structure
- Use consistent naming conventions
- Organize by project-level and template-level
- Maintain clear documentation hierarchy

### 5. Memory Management
- Use Cursor memories for important patterns and decisions
- Update documentation to maintain long-term memory
- Review memories regularly for accuracy
- Create memories proactively for reusable patterns

## Rule Updates

When updating rules:
1. Update the relevant rule file
2. Update this README if structure changes
3. Note changes in project CHANGE_LOGS.md
4. Ensure rules remain consistent with each other

## Compliance

All rules are marked with "COMPLIANCE CONFIRMED" sections. These indicate that the AI assistant has acknowledged and will follow these rules.

**Violating any rule marked as MANDATORY will invalidate the response.**

---

**Last Updated**: 2025-11-28  
**Version**: 1.0
