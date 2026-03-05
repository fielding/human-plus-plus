local config = require('human-plus-plus.config')

local M = {}

local ns = vim.api.nvim_create_namespace('hpp_headings')

-- ATX heading patterns: ^#{level} followed by space and content
local HEADING_PATTERNS = {
  { pat = '^#%s+.+$',      hl = 'HppMarkdownH1' },
  { pat = '^##%s+.+$',     hl = 'HppMarkdownH2' },
  { pat = '^###%s+.+$',    hl = 'HppMarkdownH3' },
  { pat = '^####%s+.+$',   hl = 'HppMarkdownH4' },
  { pat = '^#####%s+.+$',  hl = 'HppMarkdownH5' },
  { pat = '^######%s+.+$', hl = 'HppMarkdownH6' },
}

--- Update heading highlights for buffer.
function M.update(bufnr)
  vim.api.nvim_buf_clear_namespace(bufnr, ns, 0, -1)

  local cfg = config.options
  if not cfg.enable then return end

  -- Only markdown buffers
  if vim.bo[bufnr].filetype ~= 'markdown' then return end

  local lines = vim.api.nvim_buf_get_lines(bufnr, 0, -1, false)

  for i, line in ipairs(lines) do
    local line_num = i - 1  -- 0-indexed

    -- Check from most specific (h6) to least (h1) so longer prefix matches first
    for level = #HEADING_PATTERNS, 1, -1 do
      local hp = HEADING_PATTERNS[level]
      if line:match(hp.pat) then
        vim.api.nvim_buf_set_extmark(bufnr, ns, line_num, 0, {
          end_row = line_num,
          end_col = #line,
          hl_group = hp.hl,
          hl_eol = (level == 1),
          priority = 200,
        })
        break
      end
    end
  end

  -- Setext H1: non-empty line followed by line of ===
  for i = 1, #lines - 1 do
    local next_line = lines[i + 1]
    if next_line:match('^=+%s*$') then
      local current_line = lines[i]
      if current_line:match('%S') then
        local heading_ln = i - 1
        local underline_ln = i

        vim.api.nvim_buf_set_extmark(bufnr, ns, heading_ln, 0, {
          end_row = heading_ln,
          end_col = #current_line,
          hl_group = 'HppMarkdownH1',
          hl_eol = true,
          priority = 200,
        })
        vim.api.nvim_buf_set_extmark(bufnr, ns, underline_ln, 0, {
          end_row = underline_ln,
          end_col = #next_line,
          hl_group = 'HppMarkdownH1',
          hl_eol = true,
          priority = 200,
        })
      end
    end
  end

  -- Setext H2: non-empty line followed by line of ---
  for i = 1, #lines - 1 do
    local next_line = lines[i + 1]
    if next_line:match('^%-%-+%s*$') then
      local current_line = lines[i]
      if current_line:match('%S') then
        local heading_ln = i - 1
        local underline_ln = i

        vim.api.nvim_buf_set_extmark(bufnr, ns, heading_ln, 0, {
          end_row = heading_ln,
          end_col = #current_line,
          hl_group = 'HppMarkdownH2',
          priority = 200,
        })
        vim.api.nvim_buf_set_extmark(bufnr, ns, underline_ln, 0, {
          end_row = underline_ln,
          end_col = #next_line,
          hl_group = 'HppMarkdownH2',
          priority = 200,
        })
      end
    end
  end
end

--- Clear heading highlights from buffer.
function M.clear(bufnr)
  vim.api.nvim_buf_clear_namespace(bufnr, ns, 0, -1)
end

return M
