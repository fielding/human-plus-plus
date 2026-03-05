local config = require('human-plus-plus.config')

local M = {}

local ns = vim.api.nvim_create_namespace('hpp_markers')

-- Marker definitions matching VS Code extension exactly
local MARKERS = {
  { name = 'intervention', pattern = '!!', hl = 'HppMarkerIntervention', priority = 1 },
  { name = 'uncertainty',  pattern = '??', hl = 'HppMarkerUncertainty',  priority = 2 },
  { name = 'directive',    pattern = '>>', hl = 'HppMarkerDirective',    priority = 3 },
}

-- Keyword aliases (case-insensitive, word-boundary match)
local KEYWORDS = {
  intervention = { 'FIXME', 'BUG', 'XXX' },
  uncertainty  = { 'TODO', 'HACK' },
  directive    = { 'NOTE', 'NB' },
}

-- Regex fallback: comment prefix patterns (order matters — first match wins)
-- Mirrors COMMENT_PATTERNS from extension.ts L77-L88
local COMMENT_PATTERNS = {
  { pat = '^(%s*)(///)',              prefix_groups = 2 },  -- doc comments
  { pat = '^(%s*)(//)',              prefix_groups = 2 },  -- C-style
  { pat = '^(%s*)(#)',               prefix_groups = 2 },  -- Python/Shell/Ruby
  { pat = '^(%s*)(%-%-)',            prefix_groups = 2 },  -- SQL/Lua/Haskell
  { pat = '^(%s*)(;)',               prefix_groups = 2 },  -- Lisp/Assembly
  { pat = '^(%s*)(/[%*]+)',          prefix_groups = 2 },  -- /* block start
  { pat = '^(%s*)(%*)',              prefix_groups = 2 },  -- * block continuation
  { pat = '^(%s*)(<!%-%-)',          prefix_groups = 2 },  -- HTML/XML
  { pat = '^(%s*)(%%)',              prefix_groups = 2 },  -- LaTeX/Prolog
  { pat = '^(%s*)([Rr][Ee][Mm]%s)',  prefix_groups = 2 },  -- Basic/Batch
}

--- Try to detect if a line is a comment using Treesitter.
--- Returns the start column of the comment node, or nil.
local function ts_comment_start(bufnr, line_num)
  local ok, parser = pcall(vim.treesitter.get_parser, bufnr)
  if not ok or not parser then return nil end

  -- Parse to ensure tree is current
  local trees = parser:parse()
  if not trees or not trees[1] then return nil end

  -- Get the smallest named node at the start of the line
  local line_text = vim.api.nvim_buf_get_lines(bufnr, line_num, line_num + 1, false)[1]
  if not line_text then return nil end

  -- Find first non-whitespace column
  local first_nonws = line_text:find('%S')
  if not first_nonws then return nil end
  local col = first_nonws - 1  -- 0-indexed

  local node = vim.treesitter.get_node({ bufnr = bufnr, pos = { line_num, col } })
  if not node then return nil end

  -- Walk up to find a comment node
  local current = node
  while current do
    local ntype = current:type()
    if ntype:match('comment') then
      local sr, sc = current:start()
      if sr == line_num then
        return sc
      end
    end
    current = current:parent()
  end

  return nil
end

--- Regex fallback: detect comment prefix and return (start_col, prefix_end_col).
--- start_col = beginning of comment symbol (after leading whitespace)
--- prefix_end_col = end of comment prefix (before content)
local function regex_comment_detect(line_text)
  for _, cp in ipairs(COMMENT_PATTERNS) do
    local ws, prefix = line_text:match(cp.pat)
    if ws then
      local start_col = #ws
      local prefix_end = #ws + #prefix
      return start_col, prefix_end
    end
  end
  return nil, nil
end

--- Check for explicit marker patterns in comment content text.
--- Returns marker name or nil.
local function find_explicit_marker(content_text, enabled)
  for _, mdef in ipairs(MARKERS) do
    if enabled[mdef.name] then
      -- Escape pattern chars for Lua matching
      local escaped = mdef.pattern:gsub('([%?%.%+%-%*%[%]%(%)%^%$%%])', '%%%1')
      -- Match: optional whitespace, then the marker, then whitespace or end of string
      if content_text:match('^%s*' .. escaped .. '%s') or
         content_text:match('^%s*' .. escaped .. '$') then
        return mdef.name
      end
    end
  end
  return nil
end

--- Check for keyword aliases in comment content text.
--- Returns the strongest (lowest priority) matching marker name, or nil.
local function find_keyword_match(content_text, enabled)
  local best_name, best_priority = nil, math.huge

  for _, mdef in ipairs(MARKERS) do
    if enabled[mdef.name] then
      local keywords = KEYWORDS[mdef.name]
      if keywords then
        for _, kw in ipairs(keywords) do
          -- Case-insensitive word boundary match using %f frontier patterns
          local lower_text = content_text:lower()
          local lower_kw = kw:lower()
          if lower_text:match('%f[%w]' .. lower_kw .. '%f[%W]') then
            if mdef.priority < best_priority then
              best_name = mdef.name
              best_priority = mdef.priority
            end
            break  -- found this type, check next for potentially stronger
          end
        end
      end
    end
  end

  return best_name
end

--- Get highlight group for a marker name.
local function marker_hl(name)
  for _, mdef in ipairs(MARKERS) do
    if mdef.name == name then return mdef.hl end
  end
  return nil
end

-- Prose filetypes: markers scanned on all lines (no comment gate required).
-- >> is excluded in these filetypes to avoid conflicts with blockquotes.
local PROSE_FILETYPES = {
  markdown = true,
  text = true,
  vimwiki = true,
}

--- Scan a line in prose mode (no comment requirement).
--- Returns (marker_name, marker_start_col) or (nil, nil).
--- Skips 'directive' (>>) to avoid blockquote clash.
local function scan_prose_line(line_text, enabled)
  -- Build prose-safe enabled map (exclude directive/>>)
  local prose_enabled = {}
  for k, v in pairs(enabled) do
    if k ~= 'directive' then
      prose_enabled[k] = v
    end
  end

  -- Check explicit markers first — must be at start of line (after optional whitespace)
  for _, mdef in ipairs(MARKERS) do
    if prose_enabled[mdef.name] then
      local escaped = mdef.pattern:gsub('([%?%.%+%-%*%[%]%(%)%^%$%%])', '%%%1')
      local ws, _ = line_text:match('^(%s*)(' .. escaped .. ')')
      if ws then
        return mdef.name, #ws  -- 0-indexed start of marker
      end
    end
  end

  -- Then keyword aliases — must also be at start of line (after optional whitespace)
  -- Matches patterns like: TODO: ..., FIXME ..., etc.
  local best_name, best_priority, best_pos = nil, math.huge, nil
  for _, mdef in ipairs(MARKERS) do
    if prose_enabled[mdef.name] then
      local keywords = KEYWORDS[mdef.name]
      if keywords then
        for _, kw in ipairs(keywords) do
          local ws = line_text:match('^(%s*)' .. kw .. '%f[%W]')
          if ws and mdef.priority < best_priority then
            best_name = mdef.name
            best_priority = mdef.priority
            best_pos = #ws  -- 0-indexed
            break
          end
        end
      end
    end
  end

  return best_name, best_pos
end

--- Scan buffer for marker matches.
--- Returns list of { type, line, start_col, end_col }
function M.scan(bufnr)
  local cfg = config.options
  local lines = vim.api.nvim_buf_get_lines(bufnr, 0, -1, false)
  local matches = {}

  -- Build enabled map
  local enabled = {}
  for _, mdef in ipairs(MARKERS) do
    enabled[mdef.name] = cfg.markers[mdef.name].enable
  end

  -- Check if any marker is enabled
  local any_enabled = false
  for _, v in pairs(enabled) do
    if v then any_enabled = true; break end
  end
  if not any_enabled then return matches end

  local ft = vim.bo[bufnr].filetype
  local is_prose = PROSE_FILETYPES[ft] or false

  for i, line_text in ipairs(lines) do
    local line_num = i - 1  -- 0-indexed
    local mtype = nil
    local start_col = 0

    if is_prose then
      -- Prose mode: scan the whole line, no comment gate
      -- start_col = position of the marker itself
      local marker_pos
      mtype, marker_pos = scan_prose_line(line_text, enabled)
      if marker_pos then
        start_col = marker_pos
      end
    else
      -- Code mode: require comment detection
      local comment_start = ts_comment_start(bufnr, line_num)
      local prefix_end = nil

      if comment_start ~= nil then
        local _, pe = regex_comment_detect(line_text)
        prefix_end = pe
      else
        comment_start, prefix_end = regex_comment_detect(line_text)
      end

      if comment_start ~= nil then
        local content_text = ''
        if prefix_end then
          content_text = line_text:sub(prefix_end + 1)
        else
          content_text = line_text:sub(comment_start + 1)
        end

        mtype = find_explicit_marker(content_text, enabled)
        if not mtype then
          mtype = find_keyword_match(content_text, enabled)
        end
        start_col = comment_start
      end
    end

    if mtype then
      local trimmed = line_text:match('^(.-)%s*$')
      table.insert(matches, {
        type = mtype,
        line = line_num,
        start_col = start_col,
        end_col = #trimmed,
      })
    end
  end

  return matches
end

--- Apply marker extmarks to buffer.
function M.update(bufnr)
  vim.api.nvim_buf_clear_namespace(bufnr, ns, 0, -1)

  if not config.options.enable then return end

  local matches = M.scan(bufnr)
  for _, match in ipairs(matches) do
    local hl = marker_hl(match.type)
    if hl then
      vim.api.nvim_buf_set_extmark(bufnr, ns, match.line, match.start_col, {
        end_col = match.end_col,
        hl_group = hl,
        priority = 200,
      })
    end
  end
end

--- Clear marker extmarks from buffer.
function M.clear(bufnr)
  vim.api.nvim_buf_clear_namespace(bufnr, ns, 0, -1)
end

return M
