import {Component, computed, inject, OnInit, signal} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {AuthenticationService} from '../common/authentication/authentication.service';
import {getOAuthClientInfoView, OAuthClientInfo, oAuthApproveView} from '../../generated-files/api/mcp';

const OAUTH_PARAM_KEYS = [
  'client_id', 'redirect_uri', 'scope', 'state',
  'code_challenge', 'code_challenge_method', 'resource',
] as const;

@Component({
  selector: 'app-connect-claude',
  imports: [],
  templateUrl: './connect-claude.component.html',
})
export class ConnectClaudeComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  readonly authService = inject(AuthenticationService);

  readonly isSubmitting = signal(false);
  readonly hasValidRequest = signal(true);
  readonly clientInfo = signal<OAuthClientInfo | null>(null);

  readonly userLabel = computed(() => {
    const user = this.authService.user();
    return user?.email || user?.username || '';
  });

  private readonly params: Record<string, string> = {};

  async ngOnInit(): Promise<void> {
    const query = this.route.snapshot.queryParamMap;
    for (const key of OAUTH_PARAM_KEYS) {
      this.params[key] = query.get(key) ?? '';
    }
    if (!this.params['client_id'] || !this.params['redirect_uri']) {
      this.hasValidRequest.set(false);
      return;
    }
    if (!this.authService.isLoggedIn()) {
      await this.router.navigate(['/login'], {queryParams: {redirect: this.router.url}});
      return;
    }
    const {data} = await getOAuthClientInfoView({
      query: {client_id: this.params['client_id'], redirect_uri: this.params['redirect_uri']},
    });
    if (data) {
      this.clientInfo.set(data);
    } else {
      this.hasValidRequest.set(false);
    }
  }

  async allow(): Promise<void> {
    await this.submit(true);
  }

  async deny(): Promise<void> {
    await this.submit(false);
  }

  private async submit(approve: boolean): Promise<void> {
    this.isSubmitting.set(true);
    try {
      const {data} = await oAuthApproveView({
        body: {
          client_id: this.params['client_id'],
          redirect_uri: this.params['redirect_uri'],
          scope: this.params['scope'],
          state: this.params['state'],
          code_challenge: this.params['code_challenge'],
          code_challenge_method: this.params['code_challenge_method'],
          resource: this.params['resource'],
          approve,
        },
      });
      if (data?.redirect_url) {
        window.location.href = data.redirect_url;
      } else {
        this.isSubmitting.set(false);
      }
    } catch {
      this.isSubmitting.set(false);
    }
  }
}
