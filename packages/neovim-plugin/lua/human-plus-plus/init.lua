local config = require('human-plus-plus.config')
local markers = require('human-plus-plus.markers')
local diagnostics = require('human-plus-plus.diagnostics')
local headings = require('human-plus-plus.headings')

local M = {}

local marker_timer = nil
local diag_timer = nil
local augroup = nil

local function update_all(bufnr)
  if not vim.api.nvim_buf_is_valid(bufnr) then return end
  markers.update(bufnr)
  diagnostics.update(bufnr)
  headings.update(bufnr)
end

local function clear_all(bufnr)
  if not vim.api.nvim_buf_is_valid(bufnr) then return end
  markers.clear(bufnr)
  diagnostics.clear(bufnr)
  headings.clear(bufnr)
end

local function schedule_markers(bufnr)
  if marker_timer then
    pcall(vim.fn.timer_stop, marker_timer)
  end
  marker_timer = vim.fn.timer_start(config.options.debounce_ms, function()
    vim.schedule(function()
      if vim.api.nvim_buf_is_valid(bufnr) then
        markers.update(bufnr)
      end
    end)
  end)
end

local function schedule_diagnostics(bufnr)
  if diag_timer then
    pcall(vim.fn.timer_stop, diag_timer)
  end
  diag_timer = vim.fn.timer_start(config.options.debounce_ms, function()
    vim.schedule(function()
      if vim.api.nvim_buf_is_valid(bufnr) then
        diagnostics.update(bufnr)
      end
    end)
  end)
end

function M.setup(opts)
  -- Check Neovim version
  if vim.fn.has('nvim-0.9') ~= 1 then
    vim.notify('human-plus-plus requires Neovim 0.9+', vim.log.levels.ERROR)
    return
  end

  config.setup(opts)

  -- Clean up previous autocommands if re-calling setup
  if augroup then
    vim.api.nvim_del_augroup_by_id(augroup)
  end
  augroup = vim.api.nvim_create_augroup('HumanPlusPlus', { clear = true })

  -- Enable treesitter highlighting for markdown (parser ships with neovim 0.11+)
  -- Disable conceal so markup characters (**, *, `) stay visible
  vim.api.nvim_create_autocmd('FileType', {
    group = augroup,
    pattern = { 'markdown' },
    callback = function(ev)
      if vim.treesitter.start then
        pcall(vim.treesitter.start, ev.buf)
      end
      vim.wo.conceallevel = 0
      vim.wo.winhighlight = 'Normal:HppMarkdownNormal'
    end,
  })

  -- BufEnter / BufWinEnter → full update + markdown window settings
  vim.api.nvim_create_autocmd({ 'BufEnter', 'BufWinEnter' }, {
    group = augroup,
    callback = function(ev)
      if config.options.enable then
        update_all(ev.buf)
        -- Re-apply markdown window options (may be lost on window/buffer switch)
        if vim.bo[ev.buf].filetype == 'markdown' then
          vim.wo.conceallevel = 0
          vim.wo.winhighlight = 'Normal:HppMarkdownNormal'
        end
      end
    end,
  })

  -- FileType → update headings (filetype not yet set during BufEnter)
  vim.api.nvim_create_autocmd('FileType', {
    group = augroup,
    callback = function(ev)
      if config.options.enable then
        update_all(ev.buf)
      end
    end,
  })

  -- TextChanged / TextChangedI → debounced marker update
  vim.api.nvim_create_autocmd({ 'TextChanged', 'TextChangedI' }, {
    group = augroup,
    callback = function(ev)
      if config.options.enable then
        schedule_markers(ev.buf)
      end
    end,
  })

  -- DiagnosticChanged → debounced diagnostic update
  vim.api.nvim_create_autocmd('DiagnosticChanged', {
    group = augroup,
    callback = function(ev)
      if config.options.enable then
        schedule_diagnostics(ev.buf)
      end
    end,
  })

  -- User commands
  vim.api.nvim_create_user_command('HumanPPToggle', function()
    config.options.enable = not config.options.enable
    local bufnr = vim.api.nvim_get_current_buf()
    if config.options.enable then
      update_all(bufnr)
      vim.notify('Human++ highlighting enabled')
    else
      clear_all(bufnr)
      vim.notify('Human++ highlighting disabled')
    end
  end, { desc = 'Toggle Human++ marker highlighting' })

  vim.api.nvim_create_user_command('HumanPPRefresh', function()
    if config.options.enable then
      update_all(vim.api.nvim_get_current_buf())
    end
  end, { desc = 'Refresh Human++ marker decorations' })

  -- Initial update for current buffer
  vim.schedule(function()
    local bufnr = vim.api.nvim_get_current_buf()
    if vim.api.nvim_buf_is_loaded(bufnr) and config.options.enable then
      update_all(bufnr)
    end
  end)
end

return M
