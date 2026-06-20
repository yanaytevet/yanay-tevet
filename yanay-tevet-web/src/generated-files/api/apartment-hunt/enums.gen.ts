export enum CurrencyEnum {
  NIS = 'nis',
  USD = 'usd',
  EUR = 'eur',
  GBP = 'gbp',
}

export enum ProjectAppEnum {
  APARTMENT_HUNT = 'apartment_hunt',
  RENTERS_CRM = 'renters_crm',
  VILLA_VILLEKULLA = 'villa_villekulla',
}

export enum ProjectStatusEnum {
  ACTIVE = 'active',
  FINISHED = 'finished',
}

export enum ProjectRoleEnum {
  OWNER = 'owner',
  COLLABORATOR = 'collaborator',
}

export enum ContactMethodEnum {
  FACEBOOK = 'facebook',
  WHATSAPP = 'whatsapp',
  PHONE = 'phone',
  EMAIL = 'email',
  AGENCY = 'agency',
  OTHER = 'other',
}

export enum ProspectStatusEnum {
  SAW = 'saw',
  CONTACTED = 'contacted',
  WAITING_FOR_INVITATION = 'waiting_for_invitation',
  SAW_WAITING_FOR_THEM = 'saw_waiting_for_them',
  NEED_TO_DECIDE = 'need_to_decide',
  DECLINED = 'declined',
  ACCEPTED = 'accepted',
  SIGNED = 'signed',
}
