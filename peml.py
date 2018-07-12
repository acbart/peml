'''
Primary file
'''

import re

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

__version__ = "0.1.0"

class Loader:
    #~ Constants ...............................................................

    WHITESPACE_PATTERN = (u"\u0000\u0009\u000A\u000B\u000C\u000D\u0020"
                          u"\u00A0\u2000\u2001\u2002\u2003\u2004\u2005"
                          u"\u2006\u2007\u2008\u2009\u200A\u200B\u2028"
                          u"\u2029\u202F\u205F\u3000\uFEFF")
    SLUG_BLACKLIST     = (WHITESPACE_PATTERN+u"\u005B\u005C\u005D"
                                            +u"\u007B\u007D\u003A")

    START_KEY     = re.compile(r"^([^"+SLUG_BLACKLIST+r"]+)[ \t\r]*:"
                               +r"(((\S)\4{2,})|[ \t\r]*)(.*(?:\n|\r|$))",
                               re.UNICODE)
    COMMENT_LINE  = re.compile(r"^\s*(#.*(?:\n|\r|$))")
    COMMAND_KEY   = re.compile(r"^:[ \t\r]*(endskip|ignore|skip|end)(.*(?:\n|\r|$))",
                               re.IGNORECASE)
    ARRAY_ELEMENT = re.compile(r"^\s*\*[ \t\r]*(.*(?:\n|\r|$))")
    SCOPE_PATTERN = re.compile(r"^(\[|\{)[ \t\r]*([\+\.]*)[ \t\r]*([^"
                               +SLUG_BLACKLIST
                               +r"]*)[ \t\r]*(?:\]|\}).*?(\n|\r|$)",
                               re.UNICODE)


    #~ Public instance methods .................................................

    # -------------------------------------------------------------
    def __init__(self, options=None):
        self.data = self.scope = {}
        
        self.stack = []
        self.stack_scope = None
        
        self.buffer_scope = self.buffer_key = None
        self.buffer_string = ''
        self.quote_string = ''
        
        self.is_skipping = False
        self.is_quoted = False
        self.done_parsing = False
        self.depth = 0
        
        self.default_options = {
            'comments': False
        }
        if options is not None:
            self.default_options.update(options)

    # -------------------------------------------------------------
    def load(self, stream, options = None):
        if options is None:
            options = self.default_options.copy()
        else:
            options.update(self.default_options)
        
        for line in stream:
            if self.done_parsing:
                # Reached the end
                return self.data
            elif self.is_quoted:
                # We're in a text literal string
                if re.match(r"^"+self.quote_string+r"(?:\n|\r|$)"):
                    # end quote
                    self.parse_command_key('end')
                    self.is_quoted = False
                    self.quote_string = ''
                else:
                    self.parse_text(line)
            elif self.COMMENT_LINE.match(line):
                # Skip comments
                pass
            elif self.COMMAND_KEY.match(line):
                m = self.COMMAND_KEY.match(line)
                self.parse_command_key(m.group(1).lower())
            elif self.skipping:
                # should we just ignore this text, instead of parsing it?
                self.parse_text(line)
            elif (self.START_KEY.match(line) and
                  (not self.stack_scope or 
                   self.stack_scope['array_type'] != 'simple')):
                m = self.START_KEY.match(line)
                self.parse_start_key(m.group(1), m.group(3), m.group(5) or '')
            elif (self.ARRAY_ELEMENT.match(line) and self.stack_scope and
                  self.stack_scope['array'] and 
                  (self.stack_scope['array_type'] != 'complex') and
                  not self.stack_scope['flags'].match(r"\+")):
                m = self.ARRAY_ELEMENT.match(line)
                self.parse_array_element(m.group(1))
            elif self.SCOPE_PATTERN.match(line):
                m = self.SCOPE_PATTERN.match(line)
                self.parse_scope(m.group(1), m.group(2), m.group(3))
            else:
                # just plain text
                self.parse_text(line)

        # Treat all keys as multi-line
        self.parse_command_key('end')

        self.flush_buffer()
        return self.data

    # -------------------------------------------------------------
    def parse_start_key(self, key, quote, rest_of_line):
        # Treat all keys as multi-line
        self.parse_command_key('end')

        self.flush_buffer()

        self.increment_array_element(key)

        if self.stack_scope and self.stack_scope['flags'].match(r"\+"):
            key = 'value'
        
        self.buffer_key = key
        self.buffer_string = rest_of_line
        
        self.flush_buffer_into(key, replace=True)
        
        if quote is not None:
            self.is_quoted = True
            self.quote_string = quote

    # -------------------------------------------------------------
    def parse_array_element(self, value):
        # Treat all keys as multi-line
        self.parse_command_key('end')

        self.flush_buffer()

        if ('array_type' not in self.stack_scope
            or not self.stack_scope['array_type']):
            self.stack_scope['array_type'] = 'simple'
            
        self.stack_scope['array'].append('')
        self.buffer_key = self.stack_scope['array']
        self.buffer_string = value
        self.flush_buffer_into(self.stack_scope['array'], replace=True)

    # -------------------------------------------------------------
    def parse_command_key(command)
      if self.is_skipping && !%w(endskip ignore).include?(command)
        return self.flush_buffer!
      end

      case command
        when "end"
          self.flush_buffer_into(self.buffer_key, replace: false) if self.buffer_key
          self.buffer_key = nil
          return

        when "ignore"
          # If this occurs in the middle of a multi-line value, save what
          # has been accumulated so far
          self.flush_buffer_into(self.buffer_key, replace: false) if self.buffer_key
          return self.done_parsing = true

        when "skip"
          # If this occurs in the middle of a multi-line value, save what
          # has been accumulated so far
          self.flush_buffer_into(self.buffer_key, replace: false) if self.buffer_key
          self.is_skipping = true

        when "endskip"
          self.is_skipping = false
      end

      self.flush_buffer!
    end


    # -------------------------------------------------------------
    def parse_scope(scope_type, flags, scope_key)
      # Treat all keys as multi-line
      self.parse_command_key('end')

      self.flush_buffer!

      if scope_key == ''
        last_stack_item = self.stack.pop
        self.scope = (last_stack_item ? last_stack_item[:scope] : self.data) || self.data
        self.stack_scope = self.stack.last

      elsif %w([ {).include?(scope_type)
        nesting = false
        key_scope = self.data

        if flags.match(/^\./)
          self.increment_array_element(scope_key)
          nesting = true
          key_scope = self.scope if self.stack_scope
        else
          self.scope = self.data
          self.stack = []
        end

        # Within freeforms, the `type` of nested objects and arrays is taken
        # verbatim from the `keyScope`.
        if self.stack_scope && self.stack_scope[:flags].match(/\+/)
          parsed_scope_key = scope_key

          # Outside of freeforms, dot-notation interpreted as nested data.
        else
          key_bits = scope_key.split('.')
          key_bits[0...-1].each do |bit|
            key_scope = key_scope[bit] ||= {}
          end
          parsed_scope_key = key_bits.last
        end

        # Content of nested scopes within a freeform should be stored under "value."
        if (self.stack_scope && self.stack_scope[:flags].match(/\+/) && flags.match(/\./))
          if scope_type == '['
            parsed_scope_key = 'value'
          elsif scope_type == '{'
            self.scope = self.scope[:value] = {}
          end
        end

        stack_scope_item = {
            array: nil,
            array_type: nil,
            array_first_key: nil,
            flags: flags,
            scope: self.scope
        }
        if scope_type == '['
          stack_scope_item[:array] = key_scope[parsed_scope_key] = []
          stack_scope_item[:array_type] = :freeform if flags.match(/\+/)
          if nesting
            self.stack << stack_scope_item
          else
            self.stack = [stack_scope_item]
          end
          self.stack_scope = self.stack.last

        elsif scope_type == '{'
          if nesting
            self.stack << stack_scope_item
          else
            self.scope = key_scope[parsed_scope_key] = key_scope[parsed_scope_key].is_a?(Hash) ? key_scope[parsed_scope_key] : {}
            self.stack = [stack_scope_item]
          end
          self.stack_scope = self.stack.last
        end
      end
    end


    # -------------------------------------------------------------
    def parse_text(text)
      if self.stack_scope && self.stack_scope[:flags].match(/\+/) && text.match(/[^\n\r\s]/)
        self.stack_scope[:array] << { "type" => "text", "value" => text.gsub(/(^\s*)|(\s*$)/, '') }
      else
        self.buffer_string += text
      end
    end


    # -------------------------------------------------------------
    def increment_array_element(key)
      # Special handling for arrays. If this is the start of the array, remember
      # which key was encountered first. If this is a duplicate encounter of
      # that key, start a new object.

      if self.stack_scope && self.stack_scope[:array]
        # If we're within a simple array, ignore
        self.stack_scope[:array_type] ||= :complex
        return if self.stack_scope[:array_type] == :simple

        # array_first_key may be either another key, or nil
        if self.stack_scope[:array_first_key] == nil || self.stack_scope[:array_first_key] == key
          self.stack_scope[:array] << (self.scope = {})
        end
        if (self.stack_scope[:flags].match(/\+/))
          self.scope[:type] = key
          # key = 'content'
        else
          self.stack_scope[:array_first_key] ||= key
        end
      end
    end


    # -------------------------------------------------------------
    def flush_buffer!
      result = self.buffer_string.dup
      puts "    flushed content = #{result.inspect}"
      self.buffer_string = ''
      self.buffer_key = nil
      return result
    end


    # -------------------------------------------------------------
    def flush_buffer_into(key, options = {})
      existing_buffer_key = self.buffer_key
      value = self.flush_buffer!

      if options[:replace]
        if self.is_quoted
          self.buffer_string = value
        else
          value = self.format_value(value, :replace).sub(/^\s*/, '')
          self.buffer_string = value.match(/\s*\Z/)[0]
        end
        self.buffer_key = existing_buffer_key
      else
        value = self.format_value(value, :append)
      end
      if !self.is_quoted
        value = value.sub(/\s*\Z/, '')
      end
      puts "    flushed content = #{value.inspect}"

      if key.class == Array
        key[key.length - 1] = '' if options[:replace]
        key[key.length - 1] += value

      else
        key_bits = key.split('.')
        self.buffer_scope = self.scope

        key_bits[0...-1].each do |bit|
          self.buffer_scope[bit] = {} if self.buffer_scope[bit].class == String # reset
          self.buffer_scope = self.buffer_scope[bit] ||= {}
        end

        self.buffer_scope[key_bits.last] = '' if options[:replace]
        self.buffer_scope[key_bits.last] += value
      end
    end


    # -------------------------------------------------------------
    # type can be either :replace or :append.
    # If it's :replace, then the string is assumed to be the first line of a
    # value, and no escaping takes place.
    # If we're appending to a multi-line string, escape special punctuation
    # by prepending the line with a backslash.
    # (:, [, {, *, \) surrounding the first token of any line.
    def format_value(value, type)
      # backslash-escaped leading characters have been removed in favor of
      # quoted values.
      #
      # if type == :append
      #  value.gsub!(/^(\s*)\\/, '\1')
      # end

      # puts "    after formatting = #{value.inspect}"
      value
    end

  end
end


def load(fp):
    '''
    Load the given file object of PEML data.
    
    Args:
        peml (file): A file-like object of PEML-formatted text.
    Returns:
        Dict: Structured data representation
    '''
    return Loader().load(fp)
    
def loads(peml):
    '''
    Load the given string of PEML data.
    
    Args:
        peml (str): A string of PEML-formatted text.
    Returns:
        Dict: Structured data representation
    '''
    return Loader().load(StringIO(aml))
