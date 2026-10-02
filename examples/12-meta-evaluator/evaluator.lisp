; Stage 12 reference: first meta evaluator, arithmetic / quote / if only.
; Names of arithmetic primitives are deliberately resolved through host primitive.
(define m-global (lambda () '()))
(define m-values
  (lambda (forms env depth)
    (if (null? forms) '()
      (cons (m-eval (car forms) env depth) (m-values (cdr forms) env depth)))))
(define m-eval
  (lambda (expression env depth)
    (begin
      (trace-event "meta" depth expression)
      (if (number? expression) expression
        (if (boolean? expression) expression
          (if (string? expression) expression
            (if (list? expression)
              (if (null? expression) (error "cannot evaluate empty application")
                (begin
                  (define head (car expression))
                  (define args (cdr expression))
                  (if (equal? head 'quote)
                    (if (= (length args) 1) (car args) (error "quote: expected one argument"))
                    (if (equal? head 'if)
                      (if (= (length args) 3)
                        (m-eval (if (m-eval (car args) env (+ depth 1)) (car (cdr args)) (car (cdr (cdr args)))) env (+ depth 1))
                        (error "if: expected three arguments"))
                      (if (if (equal? head '+) #t (if (equal? head '-) #t (if (equal? head '*) #t (equal? head '/))))
                        (apply (primitive head) (m-values args env (+ depth 1)))
                        (error "stage 12 meta: only arithmetic, quote, if"))))))
              (error "stage 12 meta: unknown symbol"))))))))
