; Reference evaluator: source-program evaluation is implemented in this Lisp.
; Environment = (frame-cell parent), frame-cell = (bindings), binding = (name value).
; Primitive arithmetic, lists, I/O, and source reading remain host services.
(define m-second (lambda (xs) (car (cdr xs))))
(define m-third (lambda (xs) (car (cdr (cdr xs)))))
(define m-fourth (lambda (xs) (car (cdr (cdr (cdr xs))))))
(define m-new-env (lambda (parent) (list (list '()) parent)))
(define m-bindings (lambda (env) (car (car env))))
(define m-find-binding
  (lambda (name bindings)
    (if (null? bindings) #f
      (if (equal? name (car (car bindings))) (car bindings)
        (m-find-binding name (cdr bindings))))))
(define m-find
  (lambda (name env)
    (if (null? env) (error (string-append "unknown symbol: " (symbol->string name)))
      (begin
        (define found (m-find-binding name (m-bindings env)))
        (if found found (m-find name (m-second env)))))))
(define m-lookup (lambda (name env) (m-second (m-find name env))))
; cdr returns a fresh list in this dialect; mutate a binding by replacing its value slot.
; m-replace reconstructs the binding, retaining the frame cell shared by closures.
(define m-replace
  (lambda (name value bindings)
    (if (null? bindings) '()
      (cons (if (equal? name (car (car bindings))) (list name value) (car bindings))
        (m-replace name value (cdr bindings))))))
(define m-define
  (lambda (name value env)
    (if (symbol? name)
      (begin
        (define found (m-find-binding name (m-bindings env)))
        (set-car! (car env)
          (if found (m-replace name value (m-bindings env))
            (cons (list name value) (m-bindings env))))
        name)
      (error "define: expected symbol"))))
(define m-set
  (lambda (name value env)
    (if (symbol? name)
      (if (null? env) (error (string-append "unknown symbol: " (symbol->string name)))
        (if (m-find-binding name (m-bindings env)) (m-define name value env)
          (m-set name value (m-second env))))
      (error "set!: expected symbol"))))
(define m-arity
  (lambda (args count)
    (if (= (length args) count) #t (error "meta: wrong number of arguments"))))
(define m-contains
  (lambda (name xs)
    (if (null? xs) #f
      (if (equal? name (car xs)) #t (m-contains name (cdr xs))))))
(define m-check-params
  (lambda (params)
    (if (list? params)
      (if (null? params) #t
        (if (symbol? (car params))
          (if (m-contains (car params) (cdr params)) (error "lambda: duplicate parameter")
            (m-check-params (cdr params)))
          (error "lambda: expected symbols")))
      (error "lambda: expected list"))))
(define m-bind
  (lambda (params values env)
    (if (null? params) env
      (begin
        (m-define (car params) (car values) env)
        (m-bind (cdr params) (cdr values) env)))))
(define m-install
  (lambda (names env)
    (if (null? names) env
      (begin
        (m-define (car names) (list 'primitive (car names)) env)
        (m-install (cdr names) env)))))
(define m-global
  (lambda ()
    (m-install '(+ - * / = < > not list cons car cdr null? list? symbol? number?
                 string? boolean? equal? length append set-car! string-append symbol->string
                 display newline read-line read read-all apply error)
      (m-new-env '()))))
(define m-eval-list
  (lambda (forms env depth)
    (if (null? forms) '()
      (cons (m-eval (car forms) env depth) (m-eval-list (cdr forms) env depth)))))
(define m-sequence
  (lambda (forms env depth)
    (if (null? forms) '()
      (begin
        (define result (m-eval (car forms) env depth))
        (if (null? (cdr forms)) result (m-sequence (cdr forms) env depth))))))
(define m-apply
  (lambda (function values depth)
    (if (list? function)
      (if (null? function) (error "attempt to call a non-function")
        (if (equal? (car function) 'primitive)
          (if (equal? (m-second function) 'apply)
            (begin (m-arity values 2) (m-apply (car values) (m-second values) depth))
            (apply (primitive (m-second function)) values))
          (if (equal? (car function) 'closure)
            (begin
              (m-arity values (length (m-second function)))
              (m-sequence (m-third function)
                (m-bind (m-second function) values (m-new-env (m-fourth function))) (+ depth 1)))
            (error "attempt to call a non-function"))))
      (error "attempt to call a non-function"))))
(define m-while
  (lambda (args env depth)
    (if (< (length args) 2) (error "while: expected condition and body")
      (begin
        (define result '())
        (while (m-eval (car args) env depth)
          (set! result (m-sequence (cdr args) env depth)))
        result))))
(define m-eval
  (lambda (expression env depth)
    (begin
      (trace-event "meta" depth expression)
      (if (symbol? expression) (m-lookup expression env)
        (if (list? expression)
          (if (null? expression) (error "cannot evaluate empty application; use quote")
            (begin
              (define head (car expression))
              (define args (cdr expression))
              (if (equal? head 'quote)
                (begin (m-arity args 1) (car args))
                (if (equal? head 'if)
                  (begin (m-arity args 3)
                    (m-eval (if (m-eval (car args) env (+ depth 1)) (m-second args) (m-third args)) env (+ depth 1)))
                  (if (equal? head 'define)
                    (begin (m-arity args 2)
                      (if (symbol? (car args)) (m-define (car args) (m-eval (m-second args) env (+ depth 1)) env)
                        (error "define: expected symbol")))
                    (if (equal? head 'lambda)
                      (if (< (length args) 2) (error "lambda: expected parameters and body")
                        (begin (m-check-params (car args)) (list 'closure (car args) (cdr args) env)))
                      (if (equal? head 'begin) (m-sequence args env (+ depth 1))
                        (if (equal? head 'set!)
                          (begin (m-arity args 2)
                            (if (symbol? (car args)) (m-set (car args) (m-eval (m-second args) env (+ depth 1)) env)
                              (error "set!: expected symbol")))
                          (if (equal? head 'while) (m-while args env (+ depth 1))
                            (m-apply (m-eval head env (+ depth 1)) (m-eval-list args env (+ depth 1)) depth))))))))))
          expression)))))
