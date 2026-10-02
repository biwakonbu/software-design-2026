; Runnable starter: add quote, then arithmetic applications.
(define starter-eval
  (lambda (expression)
    (if (if (number? expression) #t (if (boolean? expression) #t (string? expression)))
      expression
      (error "starter evaluator: this expression is not implemented yet"))))
(starter-eval 42)
