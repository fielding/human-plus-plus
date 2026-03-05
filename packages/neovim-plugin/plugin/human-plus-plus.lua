if vim.g.loaded_human_plus_plus then return end
vim.g.loaded_human_plus_plus = true

if vim.fn.has('nvim-0.9') ~= 1 then
  vim.api.nvim_echo({
    { 'human-plus-plus requires Neovim 0.9+', 'ErrorMsg' },
  }, true, {})
  return
end
