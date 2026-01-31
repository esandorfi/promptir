import type { HTMLAttributes } from 'react'
import { cn } from '../../lib/utils'

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'destructive'
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium',
        {
          'bg-foreground text-background': variant === 'default',
          'bg-muted text-muted-foreground': variant === 'secondary',
          'border border-border': variant === 'outline',
          'bg-destructive/10 text-destructive': variant === 'destructive',
        },
        className
      )}
      {...props}
    />
  )
}
