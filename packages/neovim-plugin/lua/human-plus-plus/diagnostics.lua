local config = require('human-plus-plus.config')

local M = {}

local ns = vim.api.nvim_create_namespace('hpp_diagnostics')

-- Severity mapping: vim.diagnostic.severity → config key, highlight group, rank
local SEVERITY = {
  [vim.diagnostic.severity.ERROR] = { key = 'error',   hl = 'HppDiagError', rank = 1 },
  [vim.diagnostic.severity.WARN]  = { key = 'warning', hl = 'HppDiagWarn',  rank = 2 },
  [vim.diagnostic.severity.INFO]  = { key = 'info',    hl = 'HppDiagInfo',  rank = 3 },
  [vim.diagnostic.severity.HINT]  = { key = 'hint',    hl = 'HppDiagHint',  rank = 4 },
}

--- Update diagnostic badges for buffer.
function M.update(bufnr)
  vim.api.nvim_buf_clear_namespace(bufnr, ns, 0, -1)

  local cfg = config.options
  if not cfg.enable or not cfg.diagnostics.enable then return end

  local diagnostics = vim.diagnostic.get(bufnr)

  -- Group by line: keep only highest severity per line
  local by_line = {}
  for _, diag in ipairs(diagnostics) do
    local line = diag.lnum
    local info = SEVERITY[diag.severity]
    if not info then goto continue end

    -- Check if this severity level is enabled
    if not cfg.diagnostics[info.key].enable then goto continue end

    if not by_line[line] or info.rank < by_line[line].rank then
      by_line[line] = {
        rank = info.rank,
        hl = info.hl,
        message = diag.message,
      }
    end

    ::continue::
  end

  -- Render virtual text badges
  for line, entry in pairs(by_line) do
    local msg = entry.message
    if #msg > 50 then
      msg = msg:sub(1, 47) .. '...'
    end

    vim.api.nvim_buf_set_extmark(bufnr, ns, line, 0, {
      virt_text = { { '  ' .. msg .. '  ', entry.hl } },
      virt_text_pos = 'eol',
      priority = 150,
    })
  end
end

--- Clear diagnostic badges from buffer.
function M.clear(bufnr)
  vim.api.nvim_buf_clear_namespace(bufnr, ns, 0, -1)
end

return M
