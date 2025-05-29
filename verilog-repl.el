;;; verilog-repl.el --- Major mode for verilog-repl
;;;

(require 'comint)

(defgroup verilog-repl nil
  "REPL for evaluating Verilog"
  :group 'external)

(defcustom verilog-repl-path "verilog-repl"
  "Path to the program used by `verilog-repl'"
  :type 'string
  :group 'verilog-repl)

(defcustom verilog-repl-arguments '()
  "Command line arguments for `verilog-repl'"
  :group 'verilog-repl)

(defvar verilog-repl-mode-map
  (let ((map (nconc (make-sparse-keymap) comint-mode-map)))
    ;; example definition
    ;; (define-key map "\t" 'completion-at-point)
    map)
  "Basic mode map for `verilog-repl'.")

(defcustom verilog-repl-prompt-regexp "^[[:alpha:]]+>"
  "Regexp matching prompt for `verilog-repl'"
  :type 'regexp
  :group 'verilog-repl)

(defcustom verilog-repl-buffer-name "*verilog-repl*"
  "Name of the buffer containing the `verilog-repl' instance"
  :type 'string
  :group 'verilog-repl)

(defun verilog-repl ()
  (interactive)
  (let* ((buffer (get-buffer-create verilog-repl-buffer-name))
         (proc-alive (comint-check-proc buffer))
         (process (get-buffer-process buffer)))
    (unless proc-alive
      (with-current-buffer buffer
        (apply 'make-comint-in-buffer "verilog-repl" buffer
               verilog-repl-path nil verilog-repl-arguments)
        (verilog-repl-mode))
      (when buffer
        (pop-to-buffer buffer)))))

(define-derived-mode verilog-repl-mode comint-mode "verilog-repl"
  "Major mode for `verilog-repl'.
    \\<verilog-repl-mode-map>"
  (setq comint-prompt-regexp verilog-repl-prompt-regexp)
  (setq comint-prompt-read-only t))

(provide 'verilog-repl)
