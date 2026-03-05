local M = {}

M.defaults = {
  enable = true,
  debounce_ms = 200,
  markers = {
    intervention = { enable = true },
    uncertainty  = { enable = true },
    directive    = { enable = true },
  },
  diagnostics = {
    enable  = true,
    error   = { enable = true },
    warning = { enable = true },
    info    = { enable = true },
    hint    = { enable = false },  -- off by default, matching VS Code
  },
  markdown = {
    headings = { enable = true },
  },
}

M.options = vim.deepcopy(M.defaults)

function M.setup(opts)
  M.options = vim.tbl_deep_extend('force', vim.deepcopy(M.defaults), opts or {})
end

return M
